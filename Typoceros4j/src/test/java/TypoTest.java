import org.junit.Test;

import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

import static org.junit.Assert.*;

public class TypoTest {

    public static String generateRandomBitStream(int length, long seed) {

        StringBuilder sb = new StringBuilder();
        Random random = new Random(seed);

        for (int i = 0; i < length; i++) {
            int bit = random.nextInt(2);
            sb.append(bit);
        }

        return sb.toString();
    }

    String[] examples = {
            "hi, how are you?",
            "Hey, How are you? Did you see the last John Cena movie?"
            , "Hi, How are you?"
            , "However, you may as well just use a function statement instead; the only advantage that a lambda offers is that you can put a function definition for a simple expression inside a larger expression."
            , "However, you may as well just use a function statement instead; the only advantage that a lambda offers is that you can put a function definition for a simple expression inside a larger expression. But the above lambda is not part of a larger expression, it is only ever part of an assignment statement, binding it to a name. That's exactly what a statement would achieve."
            , "I’ve toyed with the idea of using GPT-3’s API to add much more intelligent capabilities to RC, but I can’t deny that I’m drawn to the idea of running this kind of language model locally and in an environment I control. I’d like to someday increase the speed of RC’s speech synthesis and add a speech-to-text translation model in order to achieve real-time communication between humans and the chatbot. I anticipate that with this handful of improvements, RC will be considered a fully-fledged member of our server. Often, we feel that it already is."
    };

    @Test
    public void santiyCheck() {
        assertTrue(List.of("TYPOS", "SPELLING", "GRAMMAR", "TYPOGRAPHY")
                .contains("TYPOS"));
    }

    private Stream<List<Integer>> testValues(List<Integer>spaces)
    {
        // TODO perform rigorous
        //  tests on each strings with these values
        return IntStream.range(0, Collections.max(spaces))
                .mapToObj(i -> spaces.stream()
                        .map(x -> i % x)
                        .collect(Collectors.toList()));
    }

    public void testString(String text, String bytes, boolean verbose) throws ValueError, IOException {
        System.out.println(">>>>>>>>>>>Test String");
        System.out.println("text='" + text + "'");
        System.out.println("bytes='" + bytes + "'");
        var typo = new Typo(text, verbose);
        Timer.startTimer("testString: '"+text+"'");
        System.out.println("typo.spaces\t" + typo.getSpaces().toString());
        Timer.prettyPrint("testString: '"+text+"'",true);
        var byteList_rem = typo.encode_encoder(bytes);
        System.out.println("byteList_rem\t" + byteList_rem.toString());
        var encoded = typo.encode(byteList_rem._1);
        System.out.println("encoded\t" + encoded);
        var decoded_byteList = Typo.decode(encoded, verbose, null);
        System.out.println("decoded_byteList\t" + decoded_byteList);

        assertEquals(text, text, decoded_byteList._1);
        assertEquals(byteList_rem._1.size(), decoded_byteList._2.size());
        for (int i = 0; i < byteList_rem._1.size(); i++) {
            assertEquals(byteList_rem._1.get(i), decoded_byteList._2.get(i));
        }
    }

    @Test
    public void testNormalize() throws IOException {
        System.out.println("Test started");
        assertEquals("hi, how are you?", LangProxy.normalize("hi, how are yiou?", true));
        for (var ex :
                examples) {
            assertEquals(ex, LangProxy.normalize(ex, false));
        }
    }

    @Test
    public void testControl() {
        for (var ex :
                examples) {
            try {
                testString(ex, generateRandomBitStream(ex.length(), 0), false);
            } catch (ValueError | IOException e) {
                e.printStackTrace();
            }
        }
    }

    @Test
    public void testControl_idx_1() {
        var ex =
                examples[1];
        try {
            testString(ex, generateRandomBitStream(ex.length(), 0), false);
        } catch (ValueError | IOException e) {
            e.printStackTrace();
        }

    }

    @Test
    public void testWild() {
        for (var ex :
                examples) {
            try {
                testString(ex, generateRandomBitStream(ex.length(), System.currentTimeMillis()), false);
            } catch (ValueError | IOException e) {
                e.printStackTrace();
            }
        }
    }
}
