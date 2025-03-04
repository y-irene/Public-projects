/**
 * Clasa care implementeaza o structura de tip produs
 */
public class Product {
    /**
     * unique id-ul produsului
     */
    private String uniqueId;
    /**
     * denumirea produsului
     */
    private String name;
    /**
     * producatorul produsului
     */
    private Manufacturer manufacturer;
    /**
     * pretul produsului in moneda curenta a magazinului
     */
    private double price;
    /**
     * cantitatea produsului
     */
    private int quantity;
    /**
     * discountul aplicat produsului in acel moment
     */
    private Discount discount;

    /**
     * Constructor fara parametri
     */
    public Product() {
    }

    /**
     * Setter pentru unique id-ul produsului
     * @param uniqueId noul unique id al produsului
     */
    public void setUniqueId(String uniqueId) {
        this.uniqueId = uniqueId;
    }

    /**
     * Setter pentru denumirea produsului
     * @param name noua denumire a produsului
     */
    public void setName(String name) {
        this.name = name;
    }

    /**
     * Setter pentru producatorul produsului
     * @param manufacturer noul producator al produsului
     */
    public void setManufacturer(Manufacturer manufacturer) {
        this.manufacturer = manufacturer;
    }

    /**
     * Setter pentru pretul produsului
     * @param price noul pret al produsului
     */
    public void setPrice(double price) {
        this.price = price;
    }

    /**
     * Setter pentru cantitatea produsului
     * @param quantity noua cantitate a produsului
     */
    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }

    /**
     * Setter pentru discountul aplicat produsului
     * @param discount noul discount aplicat produsului
     */
    public void setDiscount(Discount discount) {
        this.discount = discount;
    }

    /**
     * Getter pentru unique id-ul produsului
     */
    public String getUniqueId() {
        return uniqueId;
    }

    /**
     * Getter pentru denumirea produsului
     */
    public String getName() {
        return name;
    }

    /**
     * Getter pentru producatorul produsului
     */
    public Manufacturer getManufacturer() {
        return manufacturer;
    }

    /**
     * Getter pentru pretul produsului
     */
    public double getPrice() {
        return price;
    }

    /**
     * Getter pentru cantitatea produsului
     */
    public int getQuantity() {
        return quantity;
    }

    /**
     * Getter pentru discountul aplicat produsului
     */
    public Discount getDiscount() {
        return discount;
    }

    /**
     * Metoda afiseaza informatiile despre produs, in formatul cerut
     * @param currency moneda curenta a magazinului, in care este memorat pretul produsului
     */
    public void showProduct (Currency currency) {
        System.out.print("\t" + uniqueId + "," + name + ",");
        if (!manufacturer.getName().equals("Not Available"))
            System.out.print(manufacturer.getName() + ",");
        else
            System.out.print(",");
        System.out.println(currency.getSymbol() + price + "," + quantity);
    }
}
