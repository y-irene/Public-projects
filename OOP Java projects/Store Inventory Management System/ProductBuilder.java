/**
 * Clasa ProductBuilder implementeaza design pattern-ul Builder
 */
public class ProductBuilder {
    /**
     * Obiect de tipul Product
     */
    private Product product = new Product();

    /**
     * Metoda seteaza unique id-ul produsului
     * @param uniqueId unique id-ul produsului
     */
    public ProductBuilder withUniqueId (String uniqueId) {
        product.setUniqueId(uniqueId);
        return this;
    }

    /**
     * Metoda seteaza denumirea produsului
     * @param name denumirea produsului
     */
    public ProductBuilder withName (String name) {
        product.setName(name);
        return this;
    }

    /**
     * Metoda seteaza producatorul produsului
     * @param manufacturer producatorul produsului
     */
    public ProductBuilder withManufacturer (Manufacturer manufacturer) {
        product.setManufacturer(manufacturer);
        return this;
    }

    /**
     * Metoda seteaza pretul produsului
     * @param price pretul produsului
     */
    public ProductBuilder withPrice (double price) {
        product.setPrice(price);
        return this;
    }

    /**
     * Metoda seteaza cantitatea produsului valabila pe stoc
     * @param quantity cantitatea produsului valabila pe stoc
     */
    public ProductBuilder withQuantity (int quantity) {
        product.setQuantity(quantity);
        return this;
    }

    /**
     * Metoda seteaza discountul aplicat produsului
     * @param discount discountul aplicat produsului
     */
    public ProductBuilder withDiscount (Discount discount) {
        product.setDiscount(discount);
        return this;
    }

    /**
     * Metoda care intoarce referinta la produs
     * @return produsul
     */
    public Product build () {
        return product;
    }
}