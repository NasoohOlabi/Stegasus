import io.vavr.Tuple2;
import io.vavr.Tuple3;
import org.languagetool.JLanguageTool;
import org.languagetool.language.AmericanEnglish;
import org.languagetool.rules.RuleMatch;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class LangProxy {

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

    public static boolean word_we_misspelled(String word, String spelling, boolean verbose) {
        int uls = util.countUppercaseLetters(word);
        if (util.stringMutationDistance(spelling, word) == 1
                && Character.toLowerCase(spelling.charAt(0)) == Character.toLowerCase(word.charAt(0))
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
        List<RuleMatch> subset = new ArrayList<RuleMatch>();
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

    private static List<String> getAffectecWords(String text, StringSpans text_sss, List<Integer> offsets) {
        List<String> affected_words = new ArrayList<String>();
        for (int o : offsets) {
            String closest_word = null;
            int closest_distance = Integer.MAX_VALUE;

            for (var word : text_sss.getWords()) {
                int s = word._1;
                int e = word._2;
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
                    closest_distance = 0;
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
        List<Tuple2<Integer, Integer>> chunks = util.chunk(text, 6);
        String to_be_original = text;
        var offsets = correction_rules_subset(text, verbose).stream().map(RuleMatch::getFromPos).collect(Collectors.toList());
        boolean[] empty_chunks = new boolean[chunks.size()];
        StringSpans text_sss = new StringSpans(text);
        List<String> affected_words = getAffectecWords(text, text_sss, offsets);
        if (verbose) {
            System.out.println("text=" + text);
            System.out.println("chunks=" + chunks);
            System.out.println("offsets=" + offsets);
            System.out.println("text_sss.words=" + text_sss.getWords());
            System.out.println("affected_words=" + affected_words);
        }
        List<List<Tuple3<Integer, String, List<String>>>> offsets_chunks = new ArrayList<List<Tuple3<Integer, String, List<String>>>>();
        for (Tuple2<Integer, Integer> chunk : chunks) {
            int chunk_start = chunk._1;
            int chunk_end = chunk._2;
            List<Tuple3<Integer, String, List<String>>> chunk_offsets = new ArrayList<Tuple3<Integer, String, List<String>>>();
            for (int i = 0; i < offsets.size(); i++) {
                int o = offsets.get(i);
                if (chunk_start <= o && o < chunk_end) {
                    String affected_word = affected_words.get(i);
                    List<String> affected_word_corrections = corrections(affected_word, verbose);
                    chunk_offsets.add(new Tuple3<Integer, String, List<String>>(o, affected_word, affected_word_corrections));
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
            List<Tuple3<Integer, String, List<String>>> offsets_chunk = offsets_chunks.get(i);
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
                if (verbose)
                    System.out.println(
                            "no suggestions for " +
                                    offsets_chunk.get(0)._2 +
                                    " added to dict");
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

    public static List<String> corrections(String typo, boolean verbose) throws IOException {
        String suggestion = spellWord(typo);
        List<String> votes = new ArrayList<>();
        if (util.stringMutationDistance(suggestion, typo) == 1 && normal_word(suggestion)) {
            votes.add(suggestion);
        }
        for (var rule : Rules.FAT_CORRECTION_RULES) {
            Matcher matcher = rule._1().matcher(typo);
            while (matcher.find()) {
                var span = new Tuple2<>(matcher.start(), matcher.end());
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
                var span = new Tuple2<>(matcher.start(), matcher.end());
                votes.add(applyMatch(typo, rule, span, verbose));
            }
        }
        if (verbose) {
            System.out.println("unfiltered votes: " + votes);
        }
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

    public static String spellWord(String word) throws IOException {
        Timer.startTimer("spellWord " + word);
        List<RuleMatch> result = LangProxy.langTool.check(word);
        Timer.prettyPrint("spellWord " + word);
        if (result.size() > 0) {
            // TODO:
            /**
             * java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0
             *
             * 	at java.base/jdk.internal.util.Preconditions.outOfBounds(Preconditions.java:64)
             * 	at java.base/jdk.internal.util.Preconditions.outOfBoundsCheckIndex(Preconditions.java:70)
             * 	at java.base/jdk.internal.util.Preconditions.checkIndex(Preconditions.java:248)
             * 	at java.base/java.util.Objects.checkIndex(Objects.java:359)
             * 	at java.base/java.util.ArrayList.get(ArrayList.java:427)
             * 	at java.base/java.util.Collections$UnmodifiableList.get(Collections.java:1321)
             * 	at LangProxy.spellWord(LangProxy.java:247)
             * 	at LangProxy.corrections(LangProxy.java:200)
             * 	at LangProxy.valid_matches(LangProxy.java:364)
             * 	at LangProxy.valid_rules_scan(LangProxy.java:428)
             * 	at Typo.getSlots(Typo.java:25)
             * 	at Typo.getSpaces(Typo.java:42)
             */
            return result.get(0).getSuggestedReplacements().get(0);
        }
        return word;
    }

    public static boolean normal_word(String word) throws IOException {
        Timer.startTimer("normal_word " + word);
        List<RuleMatch> result = LangProxy.langTool.check(word);
        Timer.prettyPrint("normal_word " + word);
        return result.size() == 0;
    }

    public static String applyMatch(
            String text, String repl, Pattern regex, Tuple2<Integer, Integer> span, boolean verbose) {
        if (verbose) {
            System.out.println("text='" + text + "'");
            System.out.println("repl='" + repl + "'");
            System.out.println("regex='" + regex + "'");
            System.out.println("span='" + span + "'");
            System.out.println("Before replace: " + text);
        }

        var replaced_text = regex.matcher(text.substring(span._1, span._2)).replaceAll(repl);

        var after_replace_text = text.substring(0, span._1) + replaced_text + text.substring(span._2);
//        if (verbose)
//            System.out.println("After replace: "+after_replace_text);

        return after_replace_text;
    }

    public static String applyMatch(
            String text, Tuple2<Pattern, String> rule, Tuple2<Integer, Integer> span, boolean verbose) {
        var repl = rule._2;
        var regex = rule._1;
        return applyMatch(text, repl, regex, span, verbose);
    }

    public static String applyMatch(
            String text, Tuple3<Tuple2<Integer, Integer>, String, Pattern> rule, boolean verbose) {
        var repl = rule._2;
        var regex = rule._3;
        var span = rule._1;
        return applyMatch(text, repl, regex, span, verbose);
    }

    public static void addWord(String s) {
    }

    public static Tuple3<Tuple2<Integer, Integer>, Tuple2<Integer, Integer>, Integer> expand_span_to_word(
            List<Tuple2<Integer, Integer>> words, Tuple2<Integer, Integer> span) {
        return expand_span_to_word(words, span, false);
    }

    /**
     * @param words
     * @param span
     * @return <word_span,  relative_span, word_span_idx>
     */
    public static Tuple3<Tuple2<Integer, Integer>, Tuple2<Integer, Integer>, Integer> expand_span_to_word(
            List<Tuple2<Integer, Integer>> words, Tuple2<Integer, Integer> span, boolean verbose) {
        int ss = span._1;
        int se = span._2;

        Tuple3<Tuple2<Integer, Integer>, Tuple2<Integer, Integer>, Integer> returnValue = null;
        for (int i = 0; i < words.size(); i++) {
            var word = words.get(i);
            int start = word._1;
            int end = word._2;

            if (start <= ss && se <= end) {
                // start ss se end
                var firstTuple = new Tuple2<>(start, end);
                var secondTuple = new Tuple2<>(ss - start, se - start);
                returnValue = new Tuple3<>(firstTuple, secondTuple, i);
            } else if (ss < start && start < se && se <= end) {
                // ss start se end
                var firstTuple = new Tuple2<>(start, end);
                var secondTuple = new Tuple2<>(0, se - start);
                if (returnValue == null)
                    returnValue = new Tuple3<>(firstTuple, secondTuple, i);
            } else if (start <= ss && ss < end && end < se) {
                // start ss end se
                var firstTuple = new Tuple2<>(start, end);
                var secondTuple = new Tuple2<>(ss - start, end - start);
                if (returnValue == null)
                    returnValue = new Tuple3<>(firstTuple, secondTuple, i);
            }
        }
        if (verbose) {
            System.out.println("expand_span_to_word(" + words + "," + span + ")=" + returnValue + "");
        }
        if (returnValue != null)
            return returnValue;
        else
            throw new IllegalArgumentException("Something is wrong");
    }

    public static List<Tuple3<Tuple2<Integer, Integer>, String, Pattern>>
    valid_matches(String text, List<Tuple3<Tuple2<Integer, Integer>, String, Pattern>> slots, boolean verbose) throws IOException {
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
            var expanded = expand_span_to_word(texas.getWords(), span);
            var ex_span = expanded._1;
            var relative_span = expanded._2;
            var ex_span_index = expanded._3;
            String old_word = texas.get(ex_span);

            String new_word = applyMatch(old_word, repl, regex, relative_span, verbose);
            List<String> new_word_corrections = corrections(new_word, verbose);
            String new_word_corrections_mode;
            if (new_word_corrections.size() > 0) {
                new_word_corrections_mode = util.mode(new_word_corrections);
            } else {
                if (verbose) {
                    System.out.println("new_word: " + new_word + " can't be fixed");
                }
                new_word_corrections_mode = "";
            }
            if (normal_word(old_word) &&
                    !normal_word(new_word) &&
                    Character.toLowerCase(new_word.charAt(0)) == Character.toLowerCase(old_word.charAt(0)) &&
                    (Character.toLowerCase(new_word.charAt(new_word.length() - 1))
                            == Character.toLowerCase(old_word.charAt(old_word.length() - 1))) &&
                    new_word_corrections_mode.equals(old_word)) {
                mutations.set(match_index, texas.replace_word(ex_span_index, new_word));
            } else {
                if (verbose) {
                    System.out.println("rule undetectable or modify looks! new word \"" + new_word + "\" != \"" + old_word + "\" original and will be corrected to " + new_word_corrections_mode + " from " + new_word_corrections);
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
        List<Tuple3<Tuple2<Integer, Integer>, String, Pattern>> valid_slots = new ArrayList<>();
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

    static List<Tuple3<Tuple2<Integer, Integer>, String, Pattern>> valid_rules_scan(String text, boolean verbose) throws IOException {
        List<Tuple3<Tuple2<Integer, Integer>, String, Pattern>> proposed_slots = Rules.rules_scan(text);
        if (verbose) {
            System.out.println("proposed_slots: " + proposed_slots);
        }
        List<Tuple3<Tuple2<Integer, Integer>, String, Pattern>> valid_slots = valid_matches(text, proposed_slots, verbose);
        if (verbose) {
            System.out.println("valid_slots: ");
            for (var s : valid_slots) {
                System.out.println(s);
            }
        }
        return valid_slots;
    }
}
