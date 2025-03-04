import java.time.LocalDateTime;

/**
 * Clasa Discount implementeaza o structura de tip discount
 */
public class Discount {
    /**
     * denumirea discountului
     */
    private String name;
    /**
     * tipul discountului
     */
    private DiscountType discountType;
    /**
     * valoarea discountului
     */
    private double value;
    /**
     * data la care a fost aplicat discountul pentru prima data
     */
    private LocalDateTime lastDateApplied;

    /**
     * Constructor fara parametri
     */
    public Discount() {
    }

    /**
     * Constructor cu o parte din parametri
     * @param discountType tipul discountului
     * @param value valoarea discountului
     */
    public Discount(DiscountType discountType, double value) {
        this.discountType = discountType;
        this.value = value;
    }

    /**
     * Constructor cu toti parametrii, in afara de data aplicarii, intrucat aceasta este seatata doar la aplicarea
     * discountului
     * @param name denumirea discountului
     * @param discountType tipul discountului
     * @param value valoarea discountului
     */
    public Discount(String name, DiscountType discountType, double value) {
        this.name = name;
        this.discountType = discountType;
        this.value = value;
    }

    /**
     * Setter pentru denumirea discountului
     * @param name noua denumire a discountului
     */
    public void setName(String name) {
        this.name = name;
    }

    /**
     * Setter pentru tipul discountului
     * @param discountType noul tip al discountului
     */
    public void setDiscountType(DiscountType discountType) {
        this.discountType = discountType;
    }

    /**
     * Setter pentru valoarea discountului
     * @param value noua valoare a discountului
     */
    public void setValue(double value) {
        this.value = value;
    }

    /**
     * Setter pentru data aplicarii discountului
     * @param lastDateApplied noua valoarea a datei aplicarii discountului
     */
    public void setLastDateApplied(LocalDateTime lastDateApplied) {
        this.lastDateApplied = lastDateApplied;
    }

    /**
     * Getter pentru numele discountului
     */
    public String getName() {
        return name;
    }

    /**
     * Getter pentru tipul discountului
     */
    public DiscountType getDiscountType() {
        return discountType;
    }

    /**
     * Getter pentru valoarea discountului
     */
    public double getValue() {
        return value;
    }

    /**
     * Getter pentru data aplicarii discountului
     */
    public LocalDateTime getLastDateApplied() {
        return lastDateApplied;
    }

    /**
     * Metoda apelata la introducerea comenzii "applydiscount" pentru a modifica data aplicarii discountului in data
     * si ora curenta
     */
    public void setAsAppliedNow() {
        this.lastDateApplied = LocalDateTime.now();
    }

    /**
     * Suprascrierea metodei equals
     * @param o un obiect de tipul Discount
     * @return true, daca discountul primit ca parametru are aceeasi valoare si acelasi tip cu discountul curent, sau
     *         false, altfel
     */
    public boolean equals(Object o) {
        if (this == o) return true;
        Discount discount = (Discount) o;
        return discount.value == value && discountType == discount.getDiscountType();
    }
}