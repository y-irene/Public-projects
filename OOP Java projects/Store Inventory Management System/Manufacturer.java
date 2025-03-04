/**
 * Clasa Manufacturer implementeaza o structura de tip producator
 */
public class Manufacturer implements Comparable{
    /**
     * denumirea producatorului
     */
    private String name;
    /**
     * numarul de produse produse de producator
     */
    private int countProducts;

    /**
     * Constructor cu parametru
     * @param name denumirea producatorului
     */
    public Manufacturer(String name) {
        this.name = name;
        this.countProducts = 0;
    }

    /**
     * Setter pentru denumirea producatorului
     * @param name denumirea producatorului
     */
    public void setName(String name) {
        this.name = name;
    }

    /**
     * Getter pentru denumirea producatorului
     */
    public String getName() {
        return name;
    }

    /**
     * Getter pentru numarul de produse produse de producator
     */
    public int getCountProducts() {
        return countProducts;
    }

    /**
     * Metoda ce incrementeaza numarul de produse produse de producator
     */
    public void newProductAdded() {
        this.countProducts ++;
    }

    /**
     * Suprascrierea metodei equals
     * @param obj
     * @return true, daca producatorii au acelasi nume, sau fals, in caz contrar
     */
    public boolean equals(Object obj) {
        if (obj == null)
            return false;
        if (this.name.equals(((Manufacturer)obj).getName())) {
            return true;
        }
        return false;
    }

    /**
     * Suprascrierea metodei compareTo (folosita pentru a sorta producatorii in lista de producatori din clasa Store)
     * @param o
     * @return 1, daca numele obiectului curent este "mai mare" de cat numele obiectului trimis ca parametru, 0, daca
     *         numele celor doua obiecte sunt egale, sau -1, daca numele obiectului curent este "mai mic" decat numele
     *         obiectului trimis ca parametru
     */
    public int compareTo(Object o) {
        return this.name.compareTo(((Manufacturer)o).getName());
    }
}
