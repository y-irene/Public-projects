/**
 * Exceptia DuplicateProductException este aruncata atunci cand, la introducerea pe store a unor produse, se incearca
 * adaugarea aceluiasi produs de mai multe ori
 */
public class DuplicateProductException extends Exception{
    public DuplicateProductException() {
        super("Duplicate product exception");
    }
}
