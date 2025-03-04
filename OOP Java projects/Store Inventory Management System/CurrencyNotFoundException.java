/**
 * Exceptia CurrencyNotFoundException este aruncata atunci cand se doreste schimbarea monedei curente ale unui obiect
 * de tipul Store intr-o moneda care nu exista in lista de monede ale acelui obiect
 */
public class CurrencyNotFoundException extends Exception{

    public CurrencyNotFoundException() {
        super("Currency not found");
    }
}
