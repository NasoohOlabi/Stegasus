import org.junit.Test;
import static org.junit.Assert.*;


public class SpanTest {
    @Test
    public void intersectTests(){
        assertTrue(Span.of(2,6).intersects(Span.of(2,5)));
        assertTrue(Span.of(2,5).intersects(Span.of(2,6)));
    }

    @Test
    public void a(){
        assertEquals(
                4,
                util.stringMutationDistance("ARTE","arte"));
    }
}
