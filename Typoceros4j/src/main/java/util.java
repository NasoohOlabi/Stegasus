import com.google.common.collect.Lists;
import io.vavr.Tuple2;

import java.util.*;

public class util {

    public static int countUppercaseLetters(String s) {
        int count = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c < 'a' || c > 'z') {
                count++;
            }
        }
        return count;
    }

    public static <T> T mode(List<T> iterator) {
        Map<T, Integer> countMap = new HashMap<>();

        for (var value : iterator) {
            countMap.put(value, countMap.getOrDefault(value, 0) + 1);
        }

        T mode = null;
        int maxCount = 0;

        for (Map.Entry<T, Integer> entry : countMap.entrySet()) {
            if (entry.getValue() > maxCount) {
                mode = entry.getKey();
                maxCount = entry.getValue();
            }
        }

        return mode;
    }

    public static List<Span> chunk(String text, int span_size) {
        var words = Lists.newArrayList(new StringSpans(text).getWords());
        List<Span> chunks = new ArrayList<>();
        int lastStart = 0;
        if (words.size() < span_size)
            return List.of(Span.of(0, text.length()));
        for (int i = span_size - 1; i < words.size(); i += span_size) {
            chunks.add(Span.of(lastStart, words.get(i).end));
            if (i + 1 < words.size()) {
                lastStart = words.get(i + 1).start;
            }
        }
        var lastTuple = Span.of(chunks.get(chunks.size() - 1).start, words.get(words.size() - 1).end);
        chunks.set(chunks.size() - 1, lastTuple);
        return chunks;
    }

    public static int stringMutationDistance(String s, String t) {
        int m = s.length();
        int n = t.length();
        int[][] dp = new int[m + 1][n + 1];
        for (int i = 0; i <= m; i++) {
            dp[i][0] = i;
        }
        for (int j = 0; j <= n; j++) {
            dp[0][j] = j;
        }
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                int cost = s.charAt(i - 1) == t.charAt(j - 1) ? 0 : 1;
                dp[i][j] = Math.min(Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1), dp[i - 1][j - 1] + cost);
            }
        }
        return dp[m][n];
    }

    public static int sum(List<Integer> l) {
        return l.stream().reduce(0, Integer::sum);
    }

    public static List<Tuple2<String, String>> diff(String a, String b) {
        List<String> l_a = new StringSpans(a).getWordsStrings();
        List<String> l_b = new StringSpans(b).getWordsStrings();
        List<Tuple2<String, String>> result = new ArrayList<>();
        int len = Math.min(l_a.size(), l_b.size());
        for (int i = 0; i < len; i++) {
            if (!l_a.get(i).equals(l_b.get(i))) {
                result.add(new Tuple2<>(l_a.get(i), l_b.get(i)));
            }
        }
        return result;
    }

    public static Integer log2(Integer N) {
        return (int) (Math.log(N+1) / Math.log(2));
    }
}
