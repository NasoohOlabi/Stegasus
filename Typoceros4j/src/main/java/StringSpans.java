import io.vavr.Tuple2;
import io.vavr.Tuple3;
import io.vavr.Tuple4;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.*;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

class StringSpans {
    private String string;
    private List<Span> words;
    private List<Span> spans;
    private List<Span> nonWords;
    private List<Span> nonSpaces;

    public StringSpans() {
    }

    public StringSpans(String string) {
        if (string != null) {
            this.string = string;
            this.setSpans(string);
        }
    }

    private static List<List<Span>> _getWords(String text) {
        Pattern wordRegex = Pattern.compile("[a-zA-Z'-]+");
        Pattern spaceRegex = Pattern.compile("\\s");
        List<Span> spans = new ArrayList<>();
        List<Span> words = new ArrayList<>();
        List<Span> spaces = new ArrayList<>();
        Matcher wordMatcher = wordRegex.matcher(text);
        Matcher spaceMatcher = spaceRegex.matcher(text);
        while (wordMatcher.find()) {
            // TODO  fix wordMatcher.start() == -1
            //  I don't know why but it happened
            var span = Span.of(Math.max(0,wordMatcher.start()), wordMatcher.end());
            spans.add(span);
            words.add(span);
        }
        while (spaceMatcher.find()) {
            var span = Span.of(spaceMatcher.start(), spaceMatcher.end());
            spans.add(span);
            spaces.add(span);
        }
        spans.sort(Comparator.comparing(Span::getStart));
        List<Span> result = new ArrayList<>();
        int last = 0;
        for (Span span : spans) {
            int start = span.start;
            int end = span.end;
            if (start != last) {
                result.add(Span.of(last, start));
            }
            result.add(span);
            last = end;
        }
        if (last != text.length()) {
            result.add(Span.of(last, text.length()));
        }
        List<Span> nonWords = new ArrayList<>();
        List<Span> nonSpaces = new ArrayList<>();
        for (Span span : result) {
            int start = span.start;
            int end = span.end;
            if (!words.contains(span) && !spaceRegex.matcher(text.substring(start, end)).matches()) {
                nonWords.add(span);
            }
            if (!spaces.contains(span)) {
                nonSpaces.add(span);
            }
        }
        List<List<Span>> ret = new ArrayList<>();
        ret.add(result);
        ret.add(words);
        ret.add(nonWords);
        ret.add(nonSpaces);
        return ret;
    }

    private void setSpans(String string) {
        List<List<Span>> words = StringSpans._getWords(string);
        this.spans = words.get(0);
        this.words = words.get(1);
        this.nonWords = words.get(2);
        this.nonSpaces = words.get(3);
    }

    public String get_word(int word_index) throws IllegalArgumentException {
        if (!(0 <= word_index && word_index < this.words.size())) {
            throw new IllegalArgumentException("Invalid word index: " + word_index);
        }
        var word_span = this.words.get(word_index);
        int start = word_span.start;
        int end = word_span.end;
        return this.string.substring(start, end);
    }

    public Tuple3<Span, Span, Integer> expand_span_to_word(Span span) {
        return expand_span_to_word(span, false);
    }

    /**
     * @param span the span you want to expand
     * @return <word_span,  relative_span, word_span_idx>
     */
    public Tuple3<Span, Span, Integer> expand_span_to_word(Span span, boolean verbose) {

        Tuple3<Span, Span, Integer> returnValue = null;
        for (int i = 0; i < words.size(); i++) {
            var word = words.get(i);

            var cross = word.intersection(span);
            if (cross.isPresent()){
                returnValue = new Tuple3<>(word,cross.get().map(x->x-word.start),i);
                break;
            }
        }
        if (verbose) {
            System.out.println("expand_span_to_word(" + words + "," + span + ")=" + returnValue + "");
        }
        if (returnValue != null)
            return returnValue;
        else {
            System.out.println("span="+span);
            System.out.println("words="+words);
            throw new IllegalArgumentException("Something is wrong");
        }
    }

    public Span word_span(Span span){
        return expand_span_to_word(span)._1;
    }

    public StringSpans replace_word_StringSpans(int word_index, String replacement) {
        StringSpans ss = new StringSpans();
        var word_span = this.words.get(word_index);
        ss.string = word_span.swap(this.string, replacement);
        int word_start = word_span.start;
        int word_end = word_span.end;
        int span_index = this.spans.indexOf(word_span);
        int new_len = replacement.length();
        int word_len_diff = new_len - (word_end - word_start);
        ss.words = new ArrayList<>();
        for (Span span : this.words) {
            int start = span.start;
            int end = span.end;
            if (end < word_start) {
                ss.words.add(Span.of(start, end));
            } else {
                ss.words.add(Span.of(start + word_len_diff, end + word_len_diff));
            }
        }
        ss.spans = new ArrayList<>();
        for (Span span : this.spans) {
            int start = span.start;
            int end = span.end;
            if (end < word_start) {
                ss.spans.add(Span.of(start, end));
            } else {
                ss.spans.add(Span.of(start + word_len_diff, end + word_len_diff));
            }
        }
        ss.nonWords = new ArrayList<>();
        for (Span span : this.nonWords) {
            int start = span.start;
            int end = span.end;
            if (end < word_start) {
                ss.nonWords.add(Span.of(start, end));
            } else {
                ss.nonWords.add(Span.of(start + word_len_diff, end + word_len_diff));
            }
        }
        ss.nonSpaces = new ArrayList<>();
        for (Span span : this.spans) {
            int start = span.start;
            int end = span.end;
            if (end < word_start) {
                ss.nonSpaces.add(Span.of(start, end));
            } else {
                ss.nonSpaces.add(Span.of(start + word_len_diff, end + word_len_diff));
            }
        }
        ss.words.set(word_index, Span.of(word_start, word_start + new_len));
        ss.spans.set(span_index, Span.of(word_start, word_start + new_len));
        return ss;
    }

    public List<String> getWordsStrings() {
        var word_list = new ArrayList<String>();
        for (Span span : this.words) {
            int start = span.start;
            int end = span.end;
            word_list.add(this.string.substring(start, end));
        }
        return word_list;
    }

    public List<Span> getWords() {
        return this.words;
    }

    public Iterable<Tuple4<Integer, Integer, Integer, String>> index_span_text() {
        List<Tuple4<Integer, Integer, Integer, String>> tuple_list = new ArrayList<>();
        for (int i = 0; i < this.spans.size(); i++) {
            var span = this.spans.get(i);
            int start = span.start;
            int end = span.end;
            String text = this.string.substring(start, end);
            tuple_list.add(new Tuple4<>(i, start, end, text));
        }
        return tuple_list;
    }

    public Iterable<Tuple4<Integer, Integer, Integer, String>> index_wordSpan_text() {
        var tuple_list = new ArrayList<Tuple4<Integer, Integer, Integer, String>>();
        for (int i = 0; i < this.words.size(); i++) {
            var span = this.words.get(i);
            int start = span.start;
            int end = span.end;
            String text = this.string.substring(start, end);
            tuple_list.add(new Tuple4<>(i, start, end, text));
        }
        return tuple_list;
    }

    public Span get_span_by_offset(int offset) throws IllegalArgumentException {
        for (Span span : this.spans) {
            int start = span.start;
            int end = span.end;
            if (start <= offset && offset < end) {
                return span;
            }
        }
        throw new IllegalArgumentException("offset=" + offset + " is not in any span");
    }

    public Span get_word_by_offset(int offset) throws IllegalArgumentException {
        for (Span span : this.words) {
            int start = span.start;
            int end = span.end;
            if (start <= offset && offset < end) {
                return span;
            }
        }
        throw new IllegalArgumentException("offset=" + offset + " is not in any word");
    }

}
