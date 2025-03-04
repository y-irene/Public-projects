/**
 * Clasa Currency implementeaza o structura de tipul moneda
 */
public class Currency {
    /**
     * denumirea monedei
     */
    private String name;
    /**
     * simbolul monedei
     */
    private String symbol;
    /**
     * paritatea la euro a monedei
     */
    private double parityToEur;

    /**
     * Constructor fara parametri
     */
    public Currency() {
    }

    /**
     * Constructor cu toti parametrii
     * @param name denumirea monedei
     * @param symbol simbolul monedei
     * @param parityToEur valoarea paritatii la euro
     */
    public Currency(String name, String symbol, double parityToEur) {
        this.name = name;
        this.symbol = symbol;
        this.parityToEur = parityToEur;
    }

    /**
     * Getter pentru denumirea monedei
     */
    public String getName() {
        return name;
    }

    /**
     * Getter pentru simbolul monedei
     */
    public String getSymbol() {
        return symbol;
    }

    /**
     * Getter pentru paritatea la euro a monedei
     */
    public double getParityToEur() {
        return parityToEur;
    }

    /**
     * Setter pentru denumirea monedei
     * @param name noua denumire a monedei
     */
    public void setName(String name) {
        this.name = name;
    }

    /**
     * Setter pentru simbolul monedei
     * @param symbol noul simbol al monedei
     */
    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }

    /**
     * Setter pentru paritatea la euro a monedei
     * @param parityToEur noua paritate a monedei
     */
    public void updateParity(double parityToEur) {
        this.parityToEur = parityToEur;
    }

    /**
     * Suprascrierea metodei equals
     * @param obj obiectul cu care se compara
     * @return true, daca monedele au acelasi simbol, fals, in caz contrar
     */
    public boolean equals(Object obj) {
        if (obj == null)
            return false;
        if (this == obj)
            return true;
        if (this.symbol.equals(((Currency)obj).getSymbol()))
            return true;
        return false;
    }

    /**
     * Suprascrierea metodei toString
     * @return denumirea monedei
     */
    public String toString() {
        return name;
    }
}
