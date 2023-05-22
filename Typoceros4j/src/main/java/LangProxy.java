import io.vavr.Tuple2;
import io.vavr.Tuple3;
import org.languagetool.JLanguageTool;
import org.languagetool.language.AmericanEnglish;
import org.languagetool.rules.RuleMatch;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class LangProxy {

    private final static int INTENTIONAL_TYPO_STR_DIST = 1;

    private static final JLanguageTool langTool = new JLanguageTool(new AmericanEnglish());

    public static boolean isNormalWord(String word) throws IOException {
        Timer.startTimer("isNormalWord " + word);
        List<RuleMatch> matches = langTool.check(word);
        Timer.prettyPrint("isNormalWord " + word);
        return matches.isEmpty();
    }

    public static String spell_word(String word, boolean verbose) throws IOException {
        if (normal_word(word)) {
            return word;
        }
        Timer.startTimer("spell_word " + word);
        String spellingOpt = LangProxy.langTool.check(word).get(0).getSuggestedReplacements().get(0);
        Timer.prettyPrint("spell_word " + word);
        String spelling = (spellingOpt != null) ? spellingOpt : word;
        return word_we_misspelled(word, spelling, verbose) ? spelling : word;
    }

    public static List<RuleMatch> check(String text) throws IOException {
        return langTool.check(text);
    }

    public static boolean word_we_misspelled(String word, String spelling, boolean verbose) {
        int uls = util.countUppercaseLetters(word);
        if (Character.toLowerCase(spelling.charAt(0)) == Character.toLowerCase(word.charAt(0))
                && Character.toLowerCase(spelling.charAt(spelling.length() - 1)) == Character.toLowerCase(word.charAt(word.length() - 1))
                && uls == 2
                && uls < word.length()) {

            for (var entry : Rules.FAT_CORRECTION_RULES) {
                Matcher m = entry._1.matcher(word);
                if (!m.replaceAll(entry._2).equals(spelling)) {
                    if (verbose) {
                        System.out.printf("FAT_CORRECTION_RULES (%s) (%s): %s == %s\n", entry._1, entry._2, m.replaceAll(entry._2), spelling);
                    }
                    return true;
                }
            }
            return false;
        } else {
            return false;
        }
    }

    public static List<RuleMatch> correction_rules_subset(String text, boolean verbose) throws IOException {
        Timer.startTimer("correction_rules_subset " + text);
        List<RuleMatch> matches = LangProxy.langTool.check(text);
        Timer.prettyPrint("correction_rules_subset " + text);
        if (verbose) {
            System.out.println("matches=" + matches);
        }
        var subset = new ArrayList<RuleMatch>();
        for (RuleMatch match : matches) {
            if (List.of("TYPOS", "SPELLING", "GRAMMAR", "TYPOGRAPHY")
                    .contains(match.getRule().getCategory().getId().toString())
            ) {
                subset.add(match);
            } else if (verbose) {
                System.out.println("Discarded match=" + match);
                System.out.println("Discarded match id=" + match.getRule().getCategory().getId());
            }
        }
        return subset;
    }

    private static List<String> getAffectedWords(String text, StringSpans text_sss, List<Integer> offsets) {
        var affected_words = new ArrayList<String>();
        for (int o : offsets) {
            String closest_word = null;
            int closest_distance = Integer.MAX_VALUE;

            for (var word : text_sss.getWords()) {
                int s = word.start;
                int e = word.end;
                if (o < s) {  // o is to the left of the current word
                    int distance = s - o;
                    if (distance < closest_distance) {
                        closest_distance = distance;
                        closest_word = text.substring(s, e);
                    }
                } else if (o > e) {  // o is to the right of the current word
                    int distance = o - e;
                    if (distance < closest_distance) {
                        closest_distance = distance;
                        closest_word = text.substring(s, e);
                    }
                } else {  // o is inside the current word
                    closest_word = text.substring(s, e);
                    break;
                }
            }
            affected_words.add(closest_word);
        }
        return affected_words;
    }


    public static String normalize(String text, boolean verbose) throws IOException {
        return normalize(text, verbose, false);
    }

    public static String normalize(String text, boolean verbose, boolean learn) throws IOException {
        List<Span> chunks = util.chunk(text, 6);
        String to_be_original = text;
        var offsets =
                correction_rules_subset(text, verbose)
                        .stream()
                        .map(RuleMatch::getFromPos)
                        .collect(Collectors.toList());
        boolean[] empty_chunks = new boolean[chunks.size()];
        StringSpans text_sss = new StringSpans(text);
        List<String> affected_words = getAffectedWords(text, text_sss, offsets);
        if (verbose) {
            System.out.println("text=" + text);
            System.out.println("chunks=" + chunks);
            System.out.println("offsets=" + offsets);
            System.out.println("text_sss.words=" + text_sss.getWords());
            System.out.println("affected_words=" + affected_words);
        }
        var offsets_chunks = new ArrayList<List<Tuple3<Integer, String, List<String>>>>();
        for (var chunk : chunks) {
            int chunk_start = chunk.start;
            int chunk_end = chunk.end;
            var chunk_offsets = new ArrayList<Tuple3<Integer, String, List<String>>>();
            for (int i = 0; i < offsets.size(); i++) {
                int o = offsets.get(i);
                if (chunk_start <= o && o < chunk_end) {
                    String affected_word = affected_words.get(i);
                    List<String> affected_word_corrections = word_corrections(affected_word, verbose);
                    chunk_offsets.add(new Tuple3<>(o, affected_word, affected_word_corrections));
                    if (verbose) {
                        System.out.println("Added (" + o + ", " + affected_word + ", " + affected_word_corrections + ") to chunk_offsets");
                    }
                }
            }
            offsets_chunks.add(chunk_offsets);
            if (verbose) {
                System.out.println("Added " + chunk_offsets + " to offsets_chunks");
            }
        }
        if (verbose) {
            System.out.println("chunks_offsets=" + offsets_chunks);
        }
        for (int i = 0; i < offsets_chunks.size(); i++) {
            var offsets_chunk = offsets_chunks.get(i);
            if (offsets_chunk.size() > 1) {
                if (verbose) {
                    System.out.println("len(" + offsets_chunk + ")=" + offsets_chunk.size() + " > 1");
                }
                empty_chunks[i] = true;
                if (learn) {
                    for (var x :
                            offsets_chunk) {
                        LangProxy.addWord(x._2);
                    }
                }
            } else if (offsets_chunk.size() == 1
                    && offsets_chunk.get(0)._3.size() == 0) {
                if (verbose) {
                    System.out.println(
                            "no suggestions for " +
                                    offsets_chunk.get(0)._2 +
                                    " added to dict");
                }
                empty_chunks[i] = true;
                if (learn)
                    LangProxy.addWord(offsets_chunk.get(0)._2);
            } else if (offsets_chunk.size() == 1) {
                var cs = offsets_chunk.get(0)._3;
                if (verbose) {
                    System.out.println("typo=" +
                            offsets_chunk.get(0)._2 +
                            "\nsuggestion=" +
                            util.mode(cs));
                    System.out.println("votes=" + cs);
                }
                to_be_original = to_be_original.replaceAll(
                        offsets_chunk.get(0)._2, util.mode(cs));
            } else {
                empty_chunks[i] = true;
            }
        }

        return to_be_original;
    }

    private static Optional<RuleMatch> check_pos(Span word, String text, boolean verbose) throws IOException {
        var check = LangProxy.check(text);
        if (verbose) {
            System.out.println("check result(" + word + ", " + text + "): " + check);
        }
        for (var rule :
                check) {
            var ruleSpan = Span.of(rule.getFromPos(), rule.getToPos());
            if (word.contain(ruleSpan) || word.intersects(ruleSpan)) {
                return Optional.of(rule);
            } else if (verbose) {
                System.out.println(
                        "rule not related to word " + word + " Rule " + ruleSpan);
                System.out.println(rule);
            }
        }
        return Optional.empty();
    }

    private static List<String> getSuggestions(
            String typo,
            List<String> libSuggestions) {
        return libSuggestions
                .stream()
                .filter(x -> intentionalTypo(x, typo))
                .collect(Collectors.toList());
    }

    private static Stream<String> getSuggestionsStream(
            String typo,
            List<String> libSuggestions) {
        return libSuggestions
                .stream()
                .filter(x -> intentionalTypo(x, typo));
    }

    public static String vote_fix_word(
            Span word,
            String text,
            boolean verbose) throws IOException {
        List<String> suggestions = new ArrayList<>(10);
        var context_suggestions = check_pos(word, text, verbose);
        context_suggestions.ifPresent(ruleMatch ->
                suggestions.addAll(getSuggestions(word.in(text), ruleMatch
                        .getSuggestedReplacements())
                ));
        if (verbose) {
            System.out.println("\nvote_fix_word suggestions context: " + suggestions);
        }
        suggestions.addAll(word_corrections(
                word.in(text), verbose));
        if (verbose) {
            System.out.println("\nvote_fix_word suggestions context + non: " + suggestions);
        }
        suggestions.addAll(
                suggestions
                        .stream()
                        .flatMap((correction) -> {
                            try {
                                var result =
                                        LangProxy.check_pos(word,
                                                word.swap(text, correction)
                                                , verbose);
                                if (result.isPresent()) {
                                    return getSuggestionsStream(word.in(text),
                                            result.get().getSuggestedReplacements());
                                }
                                return Stream.empty();
                            } catch (IOException e) {
                                e.printStackTrace();
                                return Stream.empty();
                            }
                        }).collect(Collectors.toList()));
        if (verbose) {
            System.out.println("\nvote_fix_word suggestions (context + non) tried out: " + suggestions);
            System.out.println(suggestions);
            if (suggestions.size() == 0) {
                System.out.println("vote_fix_word Out of Suggestions");
                System.out.println("Suggestions: " + suggestions);
                System.out.println("Word: " + word);
                System.out.println("Text: " + text);
            }
        }
        return util.mode(suggestions);
    }

    public static List<String> word_corrections(String typo, boolean verbose) throws IOException {
        var suggestion = spellWord(typo);
        List<String> votes = new ArrayList<>(suggestion);
        for (var rule : Rules.FAT_CORRECTION_RULES) {
            Matcher matcher = rule._1().matcher(typo);
            while (matcher.find()) {
                var span = Span.of(matcher.start(), matcher.end());
                votes.add(applyMatch(typo, rule, span, verbose));
            }
        }
        for (var rule : Rules.WORD_CORRECTION_RULES) {
            Matcher matcher = rule._1().matcher(typo);
            if (matcher.find()) {
                votes.add(matcher.replaceAll(rule._2));
            }
        }
        for (var rule : Rules.KEYBOARD_CORRECTION_RULES) {
            Matcher matcher = rule._1().matcher(typo);
            while (matcher.find()) {
                var span = Span.of(matcher.start(), matcher.end());
                votes.add(applyMatch(typo, rule, span, verbose));
            }
        }
        if (verbose) {
            System.out.println("unfiltered votes: " + votes);
        }
        // if correction rules were false negative
        // so they tried to correct but they were wrong
        votes.removeIf(vote -> {
            try {
                return !normal_word(vote);
            } catch (IOException e) {
                e.printStackTrace();
                return true;
            }
        });
        if (verbose) {
            System.out.println("filtered votes: " + votes);
        }
        return votes;
    }


    public static boolean intentionalTypo(String word, String typo) {
        return util.stringMutationDistance(word, typo)
                <= INTENTIONAL_TYPO_STR_DIST;
    }

    public static List<String> spellWord(String word) throws IOException {
        return spellWord(word, 1);
    }

    public static List<String> spellWord(String word, int maxExpectDistance) throws IOException {
        Timer.startTimer("spellWord " + word);
        List<RuleMatch> result = LangProxy.langTool.check(word);
        Timer.prettyPrint("spellWord " + word);
        if (result.size() > 0) {
            return getSuggestions(word,
                    result.get(0).getSuggestedReplacements());
        }
        return List.of();
    }

    public static boolean normal_word(String word) throws IOException {
        Timer.startTimer("normal_word " + word);
        List<RuleMatch> result = LangProxy.langTool.check(word);
        Timer.prettyPrint("normal_word " + word);
        return result.size() == 0;
    }

    /**
     * @param text text to replace content in
     * @param repl replace value to use with regex
     * @param regex regex to match the part that should be replaced
     * @param span the exact position of where the match should be
     * @param verbose print every step of the way
     * @return text with regex and repl applied to the right position aka span
     */
    public static String applyMatch(
            String text, String repl, Pattern regex, Span span, boolean verbose) {
        try {
            if (verbose) {
                System.out.println("text='" + text + "'");
                System.out.println("repl='" + repl + "'");
                System.out.println("regex='" + regex + "'");
                System.out.println("span='" + span + "'");
                System.out.println("Before replace: " + text);
            }

            var replaced_text = regex.matcher(span.in(text)).replaceAll(repl);

            var after_replace_text = span.swap(text, replaced_text);
            //        if (verbose)
            //            System.out.println("After replace: "+after_replace_text);

            return after_replace_text;
        } catch (Exception exp) {
            System.out.println("Exception in LangProxy.java:389 applyMatch");
            System.out.println("text:(" + text + ")");
            System.out.println("repl:(" + repl + ")");
            System.out.println("regex:(" + regex + ")");
            System.out.println("span:(" + span + ")");
            exp.printStackTrace();
            throw exp;
        }
    }

    public static String applyMatch(
            String text, Tuple2<Pattern, String> rule, Span span, boolean verbose) {
        var repl = rule._2;
        var regex = rule._1;
        return applyMatch(text, repl, regex, span, verbose);
    }

    public static String applyMatch(
            String text, Tuple3<Span, String, Pattern> rule, boolean verbose) {
        var repl = rule._2;
        var regex = rule._3;
        var span = rule._1;
        return applyMatch(text, repl, regex, span, verbose);
    }

    public static void addWord(String s) {
    }


    public static List<Tuple3<Span, String, Pattern>>
    valid_matches(String text, List<Tuple3<Span, String, Pattern>> slots, boolean verbose) throws IOException {
        StringSpans texas = new StringSpans(text);
        List<String> mutations = new ArrayList<>(slots.size());
        for (int i = 0; i < slots.size(); i++) {
            mutations.add("");
        }
        for (int match_index = 0; match_index < slots.size(); match_index++) {
            var match_result = slots.get(match_index);
            var span = match_result._1;
            String repl = match_result._2;
            Pattern regex = match_result._3;
            var expanded = texas.expand_span_to_word(span);
            var wordSpan = expanded._1;
            var relative_span = expanded._2;
            String old_word = wordSpan.in(text);

            String new_word = applyMatch(old_word, repl, regex, relative_span, verbose);
            var new_word_span = Span.of(wordSpan.start, wordSpan.start + new_word.length());

            String new_word_corrections_mode =
                    vote_fix_word(
                            new_word_span,
                            wordSpan.swap(text, new_word),
                            verbose);
            if (verbose)
                System.out.println("new_word: " + new_word + " can't be fixed");
            if (normal_word(old_word) &&
                    !normal_word(new_word) &&
                    Character.toLowerCase(new_word.charAt(0)) == Character.toLowerCase(old_word.charAt(0)) &&
                    (Character.toLowerCase(new_word.charAt(new_word.length() - 1))
                            == Character.toLowerCase(old_word.charAt(old_word.length() - 1))) &&
                    new_word_corrections_mode.equals(old_word)) {
                mutations.set(match_index, wordSpan.swap(text, new_word));
            } else {
                if (verbose) {
                    System.out.println("rule undetectable or modify looks! new word \"" + new_word + "\" != \"" + old_word + "\" original and will be corrected to " + new_word_corrections_mode);
                }
            }
        }
        List<Integer> ambiguous_invalid_matches = new ArrayList<>();
        for (int i = 0; i < mutations.size(); i++) {
            String new_string = mutations.get(i);
            if (new_string.isEmpty() ||
                    mutations.subList(0, i).contains(new_string) ||
                    !normalize(new_string, verbose).equals(text)) {
                if (verbose) {
                    System.out.println("mutation '" + new_string + "' is ambiguous because");
                    System.out.print((new_string.isEmpty()) ? "it's empty\n" : "");
                    System.out.print((mutations.subList(0, i).contains(new_string)) ? "previous slot yields the same typo\n" : "");
                    System.out.println((normalize(new_string, false).equals(text)) ?
                            "Not correctable normalize('" + new_string + "').equals('" + text + "')=" + normalize(new_string, false).equals(text) : "");
                }
                ambiguous_invalid_matches.add(i);
            }
        }
        if (verbose) {
            System.out.println("ambiguous_invalid_matches=" + ambiguous_invalid_matches);
        }
        List<Tuple3<Span, String, Pattern>> valid_slots = new ArrayList<>();
        for (int i = 0; i < slots.size(); i++) {
            if (!ambiguous_invalid_matches.contains(i)) {
                valid_slots.add(slots.get(i));
            }
        }
        if (verbose) {
            System.out.println("\n" + "%".repeat(20) + "valid slots!" + "%".repeat(20));
            System.out.println("valid_slots=" + valid_slots);
            System.out.println("\n" + "%".repeat(20) + "valid slots!" + "%".repeat(20));
            for (int i = 0; i < slots.size(); i++) {
                System.out.println(slots.get(i) + " " + mutations.get(i));
            }
        }
        return valid_slots;
    }

    static List<Tuple3<Span, String, Pattern>> valid_rules_scan(String text, boolean verbose) throws IOException {
        List<Tuple3<Span, String, Pattern>> proposed_slots = Rules.rules_scan(text);
        if (verbose) {
            System.out.println("proposed_slots: " + proposed_slots);
        }
        List<Tuple3<Span, String, Pattern>> valid_slots = valid_matches(text, proposed_slots, verbose);
        if (verbose) {
            System.out.println("valid_slots: ");
            for (var s : valid_slots) {
                System.out.println(s);
            }
        }
        return valid_slots;
    }


}
