import org.languagetool.JLanguageTool;
import org.languagetool.language.AmericanEnglish;
import org.languagetool.language.BritishEnglish;
import org.languagetool.rules.RuleMatch;

import java.io.IOException;
import java.util.*;
import java.util.stream.Collectors;

public class App {
    private static Map<String,Typo> memo = new HashMap<>();
    private static Typo getTypo(String string) throws IOException {
        if (memo.containsKey(string)){
            return memo.get(string);
        }
        Typo typo = new Typo(string);
        memo.put(string,typo);
        return typo;
    }
    public static void main(String[] args) throws IOException, ValueError {
        String command;
        String string;
        String bytes;
        Typo typo;
            Scanner scanner = new Scanner(System.in);
        while (true) {
            command = scanner.nextLine();
            string = scanner.nextLine();
            if (command.equalsIgnoreCase("encode")){
            bytes = scanner.nextLine();
                typo = getTypo(string);
                var values_remainingBytes = typo.encode_encoder(bytes);
                var values = values_remainingBytes._1();
                var remainingBytes = values_remainingBytes._2;
                System.out.println(typo.encode(values));
                System.out.println(remainingBytes);
            } else if (command.equalsIgnoreCase("decode")){
                var originalText_values = Typo.decode(string,false,null);
                var originalText = originalText_values._1();
                var values = originalText_values._2;
                System.out.println(originalText);
                System.out.println(values);
            }
        }
    }
}
