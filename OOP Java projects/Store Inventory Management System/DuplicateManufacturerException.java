/**
 * Exceptia DuplicateManufacturerException este aruncata atunci cand, la introducerea pe store a unor produse, se
 * gasesc produse cu acelasi producator, incercand sa se introduca un producator duplicat in lista de producatori
 */
public class DuplicateManufacturerException extends Exception{
    public DuplicateManufacturerException()  {
        super("Duplicate manufacturer exception");
    }
}
