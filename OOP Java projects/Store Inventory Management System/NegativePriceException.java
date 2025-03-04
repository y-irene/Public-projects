/**
 * Exceptia NegativePriceException este aruncata atunci cand la aplicarea unui discount, noul pret al produsului ar fi
 * negativ
 */
public class NegativePriceException extends Exception{
    public NegativePriceException() {
        super("Negative price");
    }
}
