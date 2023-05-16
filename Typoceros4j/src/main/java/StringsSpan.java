import io.vavr.Tuple2;
import io.vavr.Tuple4;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.*;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

class StringSpans {
    private String string;
    private List<Tuple2<Integer, Integer>> words;
    private List<Tuple2<Integer, Integer>> spans;
    private List<Tuple2<Integer, Integer>> nonWords;
    private List<Tuple2<Integer, Integer>> nonSpaces;

    public StringSpans() {
    }

    public StringSpans(String string) {
        if (string != null) {
            this.string = string;
            this.setSpans(string);
        }
    }

    private static List<List<Tuple2<Integer, Integer>>> _getWords(String text) {
        Pattern wordRegex = Pattern.compile("[a-zA-Z'-]+");
        Pattern spaceRegex = Pattern.compile("\\s");
        List<Tuple2<Integer, Integer>> spans = new ArrayList<>();
        List<Tuple2<Integer, Integer>> words = new ArrayList<>();
        List<Tuple2<Integer, Integer>> spaces = new ArrayList<>();
        Matcher wordMatcher = wordRegex.matcher(text);
        Matcher spaceMatcher = spaceRegex.matcher(text);
        while (wordMatcher.find()) {
            var span = new Tuple2(wordMatcher.start(), wordMatcher.end());
            spans.add(span);
            words.add(span);
        }
        while (spaceMatcher.find()) {
            var span = new Tuple2(spaceMatcher.start(), spaceMatcher.end());
            spans.add(span);
            spaces.add(span);
        }
        spans.sort(Comparator.comparing(Tuple2::_1));
        List<Tuple2<Integer, Integer>> result = new ArrayList<>();
        int last = 0;
        for (Tuple2<Integer, Integer> span : spans) {
            int start = span._1;
            int end = span._2;
            if (start != last) {
                result.add(new Tuple2(last, start));
            }
            result.add(span);
            last = end;
        }
        if (last != text.length()) {
            result.add(new Tuple2(last, text.length()));
        }
        List<Tuple2<Integer, Integer>> nonWords = new ArrayList<>();
        List<Tuple2<Integer, Integer>> nonSpaces = new ArrayList<>();
        for (Tuple2<Integer, Integer> span : result) {
            int start = span._1;
            int end = span._2;
            if (!words.contains(span) && !spaceRegex.matcher(text.substring(start, end)).matches()) {
                nonWords.add(span);
            }
            if (!spaces.contains(span)) {
                nonSpaces.add(span);
            }
        }
        List<List<Tuple2<Integer, Integer>>> ret = new ArrayList<>();
        ret.add(result);
        ret.add(words);
        ret.add(nonWords);
        ret.add(nonSpaces);
        return ret;
    }

    private void setSpans(String string) {
        List<List<Tuple2<Integer, Integer>>> words = StringSpans._getWords(string);
        this.spans = words.get(0);
        this.words = words.get(1);
        this.nonWords = words.get(2);
        this.nonSpaces = words.get(3);
    }

    public String replace_word(int wordIndex, String replacement) {
        if (wordIndex < 0 || wordIndex >= this.words.size()) {
            throw new IllegalArgumentException("Invalid word index: " + wordIndex);
        }
        var wordSpan = this.words.get(wordIndex);
        int start = wordSpan._1;
        int end = wordSpan._2;
        return this.string.substring(0, start) + replacement + this.string.substring(end);
    }

    public String get_word(int word_index) throws IllegalArgumentException {
        if (!(0 <= word_index && word_index < this.words.size())) {
            throw new IllegalArgumentException("Invalid word index: " + word_index);
        }
        var word_span = this.words.get(word_index);
        int start = word_span._1;
        int end = word_span._2;
        return this.string.substring(start, end);
    }

    public String get(Tuple2<Integer, Integer> span) {
        return this.string.substring(span._1, span._2);
    }

    public StringSpans replace_word_StringSpans(int word_index, String replacement) {
        StringSpans ss = new StringSpans();
        ss.string = this.replace_word(word_index, replacement);
        var word_span = this.words.get(word_index);
        int word_start = word_span._1;
        int word_end = word_span._2;
        int span_index = this.spans.indexOf(word_span);
        int new_len = replacement.length();
        int word_len_diff = new_len - (word_end - word_start);
        ss.words = new ArrayList<>();
        for (Tuple2<Integer, Integer> span : this.words) {
            int start = span._1;
            int end = span._2;
            if (end < word_start) {
                ss.words.add(new Tuple2(start, end));
            } else {
                ss.words.add(new Tuple2(start + word_len_diff, end + word_len_diff));
            }
        }
        ss.spans = new ArrayList<>();
        for (Tuple2<Integer, Integer> span : this.spans) {
            int start = span._1;
            int end = span._2;
            if (end < word_start) {
                ss.spans.add(new Tuple2(start, end));
            } else {
                ss.spans.add(new Tuple2(start + word_len_diff, end + word_len_diff));
            }
        }
        ss.nonWords = new ArrayList<>();
        for (Tuple2<Integer, Integer> span : this.nonWords) {
            int start = span._1;
            int end = span._2;
            if (end < word_start) {
                ss.nonWords.add(new Tuple2(start, end));
            } else {
                ss.nonWords.add(new Tuple2(start + word_len_diff, end + word_len_diff));
            }
        }
        ss.nonSpaces = new ArrayList<>();
        for (Tuple2<Integer, Integer> span : this.spans) {
            int start = span._1;
            int end = span._2;
            if (end < word_start) {
                ss.nonSpaces.add(new Tuple2(start, end));
            } else {
                ss.nonSpaces.add(new Tuple2(start + word_len_diff, end + word_len_diff));
            }
        }
        ss.words.set(word_index, new Tuple2(word_start, word_start + new_len));
        ss.spans.set(span_index, new Tuple2(word_start, word_start + new_len));
        return ss;
    }

    public List<String> getWordsStrings() {
        List<String> word_list = new ArrayList<String>();
        for (Tuple2<Integer, Integer> span : this.words) {
            int start = span._1;
            int end = span._2;
            word_list.add(this.string.substring(start, end));
        }
        return word_list;
    }

    public List<Tuple2<Integer,Integer>> getWords() {
        return this.words;
    }

    public Iterable<Tuple4<Integer, Integer, Integer, String>> index_span_text() {
        List<Tuple4<Integer, Integer, Integer, String>> tuple_list = new ArrayList<>();
        for (int i = 0; i < this.spans.size(); i++) {
            var span = this.spans.get(i);
            int start = span._1;
            int end = span._2;
            String text = this.string.substring(start, end);
            tuple_list.add(new Tuple4<Integer, Integer, Integer, String>(i, start, end, text));
        }
        return tuple_list;
    }

    public Iterable<Tuple4<Integer, Integer, Integer, String>> index_wordSpan_text() {
        List<Tuple4<Integer, Integer, Integer, String>> tuple_list = new ArrayList<Tuple4<Integer, Integer, Integer, String>>();
        for (int i = 0; i < this.words.size(); i++) {
            var span = this.words.get(i);
            int start = span._1;
            int end = span._2;
            String text = this.string.substring(start, end);
            tuple_list.add(new Tuple4<Integer, Integer, Integer, String>(i, start, end, text));
        }
        return tuple_list;
    }

    public Tuple2<Integer, Integer> get_span_by_offset(int offset) throws IllegalArgumentException {
        for (Tuple2<Integer, Integer> span : this.spans) {
            int start = span._1;
            int end = span._2;
            if (start <= offset && offset < end) {
                return span;
            }
        }
        throw new IllegalArgumentException("offset=" + offset + " is not in any span");
    }

    public Tuple2<Integer, Integer> get_word_by_offset(int offset) throws IllegalArgumentException {
        for (Tuple2<Integer, Integer> span : this.words) {
            int start = span._1;
            int end = span._2;
            if (start <= offset && offset < end) {
                return span;
            }
        }
        throw new IllegalArgumentException("offset=" + offset + " is not in any word");
    }

}
