import io.vavr.Tuple2;
import io.vavr.Tuple3;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.function.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

public class Rules {

    static String ROOT_DIR = "/path/to/root/dir"; // Replace with actual root directory

    static Stream<Tuple2<String, String>> parseRules(String name) {
        InputStream inputStream = Rules.class.getClassLoader().getResourceAsStream("rules/"+name+".tsv");
        assert inputStream != null;
        BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
        return reader.lines()
                .map(String::strip)
                .filter(line -> !line.isEmpty())
                .map(line -> line.split("\t"))
                .filter(line -> line.length > 1)
                .map(line -> new Tuple2<>(line[0], line[1]));
    }

    static Tuple2<Pattern, String> compileFirst(Tuple2<String, String> x) {
        try {
            return new Tuple2<>(Pattern.compile(x._1), x._2);
        } catch (PatternSyntaxException e) {
            System.err.println(x);
            throw new IllegalArgumentException("compilable " + x, e);
        }
    }

    static List<Tuple2<Pattern, String>> WORD_CORRECTION_RULES = Stream.concat(
            parseRules("anti.variant"),
            parseRules("anti.misspelling")
    ).map(Rules::compileFirst).collect(Collectors.toList());

    /**
     * these include the count rules and long shift rules
     */
    static List<Tuple2<Pattern, String>> KEYBOARD_CORRECTION_RULES = parseRules("anti.keyboard").map(Rules::compileFirst).collect(Collectors.toList());
    /**
     * these include only fat rules
     */
    static List<Tuple2<Pattern, String>> FAT_CORRECTION_RULES = parseRules("fat.keyboard").map(Rules::compileFirst).collect(Collectors.toList());

    static List<Tuple2<Pattern, String>> WORD_RULES = Stream.concat(
            parseRules("variant"),
            Stream.concat(parseRules("grammatical"), parseRules("misspelling"))
    ).map(Rules::compileFirst).collect(Collectors.toList());

    static List<Tuple2<Pattern, String>> KEYBOARD_RULES = parseRules("keyboard").map(Rules::compileFirst).collect(Collectors.toList());

    static List<Tuple3<Span,String,Pattern>> keyboard_rules_scan(String text) {
        List<Tuple3<Span,String,Pattern>> matches = new ArrayList<>();
        for (var rule : Rules.KEYBOARD_RULES) {
            Pattern regex = rule._1;
            Matcher matcher = regex.matcher(text);
            while (matcher.find()) {
                int start = matcher.start();
                int end = matcher.end();
                String replacement = rule._2;
                matches.add(new Tuple3<>(Span.of(start, end), replacement, regex));
            }
        }
        return matches;
    }

    static List<Tuple3<Span,String,Pattern>> word_rules_scan(String text) {
        List<Tuple3<Span,String,Pattern>> matches = new ArrayList<>();
        for (var rule : Rules.WORD_RULES) {
            Pattern regex = rule._1;
            Matcher matcher = regex.matcher(text);
            if (matcher.matches()) {
                int start = matcher.start();
                int end = matcher.end();
                String replacement = rule._2;
                matches.add(new Tuple3<>(Span.of(start, end), replacement, regex));
            }
        }
        return matches;
    }

    static List<Tuple3<Span,String,Pattern>> rules_scan(String text) {
        List<Tuple3<Span,String,Pattern>> result = new ArrayList<>();
        result.addAll(word_rules_scan(text));
        result.addAll(keyboard_rules_scan(text));
        result.sort((a, b) -> (a._1.start - b._1.start != 0)?a._1.start - b._1.start:a._1.end - b._1.end);
        return result;
    }
}
