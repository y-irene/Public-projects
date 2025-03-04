import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;
import java.io.*;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Clasa Store implementeaza o structura de tip magazin folosind design pattern-ul Singleton
 */
public class Store {
    /**
     * instanta unica a magazinului
     */
    private static Store uniqueInstance;
    /**
     * numele magazinului
     */
    private String name;
    /**
     * moneda curenta a magazinului
     */
    private Currency currentCurrency;
    /**
     * lista de monede posibile ale magazinului
     */
    private ArrayList<Currency> currencies;
    /**
     * lista de produse ale magazinului
     */
    private ArrayList<Product> products;
    /**
     * lista de producatori ai magazinului
     */
    private ArrayList<Manufacturer> manufacturers;
    /**
     * lista de discounturi disponibile in magazin
     */
    private ArrayList<Discount> discounts;

    /**
     * Constructor fara parametri
     */
    public Store() {
        currencies = new ArrayList<>();
        products = new ArrayList<>();
        manufacturers = new ArrayList<>();
        discounts = new ArrayList<>();
    }

    /**
     * Constrctor de initializare a instantei unice a magazinului
     * @param name denumirea magazinului
     * @return instanta unica a magazinului
     */
    public static Store Instance(String name) {
        /*
        Daca magazinul nu a fost instantiat, acesta este creat
         */
        if (uniqueInstance == null) {
            /*
            Se apeleaza constructorul magazinului
             */
            uniqueInstance = new Store();
            /*
            Se seteaza numele magazinului
             */
            uniqueInstance.setName(name);
            /*
            Se creeaza moneda euro (folosind metoda createCurrency) si se seteaza ca moneda intiala
             */
            uniqueInstance.createCurrency("EUR", "€", 1.0);
            uniqueInstance.currentCurrency = uniqueInstance.currencies.get(0);
        }
        /*
        Se intoarce referinta catre instanta unica
         */
        return uniqueInstance;
    }

    /**
     * Setter pentru numele magazinului
     * @param name noul nume al magazinului
     */
    public void setName(String name) {
        this.name = name;
    }

    /**
     * Setter pentru moneda magazinului
     * @param currency noua moneda a magazinului
     */
    public void setCurrency(Currency currency) {
        this.currentCurrency = currency;
    }

    /**
     * Setter pentru lista de monede ale magazinului
     * @param currencies noua lista de monede ale magazinului
     */
    public void setCurrencies(ArrayList<Currency> currencies) {
        this.currencies = currencies;
    }

    /**
     * Setter pentru lista de produse ale magazinului
     * @param products noua lista de produse ale magazinului
     */
    public void setProducts(ArrayList<Product> products) {
        this.products = products;
    }

    /**
     * Setter pentru lista de producatori ai magazinului
     * @param manufacturers noua lista de producatori ai magazinului
     */
    public void setManufacturers(ArrayList<Manufacturer> manufacturers) {
        this.manufacturers = manufacturers;
    }

    /**
     * Setter pentru lista de discounturi ale magazinului
     * @param discounts noua lista de discounturi ale magazinului
     */
    public void setDiscounts(ArrayList<Discount> discounts) {
        this.discounts = discounts;
    }

    /**
     * Getter pentru numele magazinului
     */
    public String getName() {
        return name;
    }

    /**
     * Getter pentru moneda curenta a magazinului
     */
    public Currency getCurrentCurrency() {
        return currentCurrency;
    }

    /**
     * Getter pentru lista de monede ale magazinului
     */
    public ArrayList<Currency> getCurrencies() {
        return currencies;
    }

    /**
     * Getter pentru lista de produse ale magazinului
     */
    public ArrayList<Product> getProducts() {
        return products;
    }

    /**
     * Getter pentru lista de producatori ai magazinului
     */
    public ArrayList<Manufacturer> getManufacturers() {
        return manufacturers;
    }

    /**
     * Getter pentru lista de discounturi ale magazinului
     */
    public ArrayList<Discount> getDiscounts() {
        return discounts;
    }

    /* CURRENCY */

    /**
     * Metoda creeaza o noua moneda si o adauga in lista de monede ale magazinului
     * @param name denumirea monedei
     * @param symbol simbolul monedei
     * @param parityToEur paritatea monedei
     * @return moneda nou creata
     */
    public Currency createCurrency (String name, String symbol, double parityToEur) {
        /*
        Se creeaza noua moneda cu informatiile primite ca parametri
         */
        Currency newCurrency = new Currency(name, symbol, parityToEur);
        /*
        Se adauga moneda nou creata in lista de monede ale magazinului
         */
        currencies.add(newCurrency);
        return newCurrency;
    }

    /**
     * Metoda cauta o moneda in lista de monede ale magazinului dupa simbolul acesteia
     * @param symbol simbolul monedei cautate
     * @return moneda cautata, daca aceasta este gasita, sau null, in caz contrar
     */
    public Currency searchCurrencyBySymbol (String symbol) {
        /*
        Se parcurge lista de monede ale magazinului
         */
        for (Currency c : currencies) {
            /*
            Daca moneda cautata a fost gasita, referinta catre aceasta este intoarsa
             */
            if (c.getSymbol().equals(symbol)){
                return c;
            }
        }
        /*
        Daca s-a ajuns in acest punct al metodei, moneda nu a fost gasita. Se intoarce null.
         */
        return null;
    }

    /**
     * Metoda cauta o moneda in lista de monede ale magazinului dupa denumirea acesteia
     * @param name denumirea monedei cautate
     * @return moneda cautata, daca aceasta este gasita, sau null, in caz contrar
     */
    public Currency searchCurrencyByName (String name) {
        /*
        Se parcurge lista de monede ale magazinului
         */
        for (Currency c : currencies) {
            /*
            Daca aceasta a fost gasita, se intoarce referinta catre aceasta
             */
            if (c.getName().equals(name)){
                return c;
            }
        }
        /*
        Daca moneda nu a fost gasit, se intoarce null
         */
        return null;
    }

    /**
     * Metoda schimba moneda curenta a magazinului intr-o moneda primita ca parametru, daca aceasat exista
     * @param currency noua moneda curenta a magazinului
     * @throws CurrencyNotFoundException daca moneda primita ca parametru nu a fost gasita in lista de monede ale
     * magazinului, se intoarce aceasat exceptie
     */
    public void changeCurrency (Currency currency) throws CurrencyNotFoundException{
        /*
        Se cauta moneda dupa nume cu ajutorul metodei searchCurrencyByName
         */
        Currency found = this.searchCurrencyByName(currency.getName());
        if (found == null) {
            /*
            Daca moneda nu a fost gasita in lista de monede ale magazinului, se arunca o exceptie de tipul
            CurrencyNotFoundException
             */
            throw new CurrencyNotFoundException();
        } else {
            /*
            Altfel, se extrag vechea paritate si noua paritate si se actualizeaza preturile produselor
             */
            double oldParity = this.currentCurrency.getParityToEur();
            double newParity = found.getParityToEur();
            this.updatePrices(oldParity, newParity);
            /*
            Se actualizeaza moneda curenta
             */
            this.setCurrency(found);
        }
    }

    /**
     * Metoda actualizeaza produsele dintr-un magazin, atunci cand moneda curenta a fost schimbata
     * @param oldParity paritatea vechii monede
     * @param newParity paritatea noii monede
     */
    public void updatePrices (double oldParity, double newParity) {
        /*
        Pentru fiecare produs se actualizeaza pretul astfel: pretul este inmultit cu vechea paritate pentru a se
        converti pretul in euro, apoi este impartit la noua paritate pentru a se trece in noua moneda
         */
        for (Product p : products){
            p.setPrice(p.getPrice() * oldParity / newParity);
        }
    }

    /* MANUFACTURERS */

    /**
     * Metoda adauga in lista de producatori ai magazinului un producator primit ca parametru
     * @param manufacturer producatorul care se adauga
     * @throws DuplicateManufacturerException daca producatorul primit ca parametru este deja in lista de producatori,
     * aceasta exceptie este aruncata
     */
    public void addManufacturer (Manufacturer manufacturer) throws DuplicateManufacturerException{
        /*
        Se verifica daca producatorul care se doreste sa fie adaugat in lista de producatori ai magazinului exista deja,
        folosind metoda serachManufacturer din clasa Store.
         */
        Manufacturer found = searchManufacturer(manufacturer);
        if (found == null) {
            /*
            Daca metoda searchManufacturer intoarce o referinta egala cu null, producatorul nu exista deja in lista
            de producatori, asa ca acesta este adaugat
             */
            manufacturers.add(manufacturer);
        } else {
            /*
            In caz contrar, se arunca o exceptie de tipul DuplicateManufacturerException
             */
            throw new DuplicateManufacturerException();
        }
    }

    /**
     * Metoda cauta un producator in lista de producatori ai magazinului
     * @param manufacturer producatorul cautat
     * @return referinta catre producator, daca acesta exista in lista de producatori deja, sau null, in caz contrar
     */
    public Manufacturer searchManufacturer (Manufacturer manufacturer) {
        /*
        Pentru fiecare producator din lista de producatori, se verifica daca acesta este cel cautat
         */
        for (Manufacturer m : manufacturers) {
            if (manufacturer.equals(m)) {
                /*
                Daca producatorul a fost gasit, se intoarce referinta catre acesta
                 */
                return m;
            }
        }
        /*
        Daca s-a ajuns in acest punct al metodei, producatorul nu a fost gasit si se intoarce null
         */
        return null;
    }

    /* PRODUCTS */

    /**
     * Metoda adauga un produs primit ca parametru in lista de produse ale magazinului
     * @param product noul produs
     * @throws DuplicateProductException daca produsul primit ca parametru exista deja in lista de produse, aceasat
     * exceptie este aruncata
     */
    public void addProduct (Product product) throws DuplicateProductException{
        /*
        Se cauta produsul care se doreste sa se adauge folosind metoda searchProduct din clasa Store
         */
        Product found = searchProduct(product.getUniqueId());
        if (found != null) {
            /*
            Daca produsul este deja in lista de produse (functia searchProduct intoarce o referinta catre produs), se
            arunca o exceptie de tipul DuplicateProductException
            */
            throw new DuplicateProductException();
        }
        /*
        Daca produsul nu a fost gasit in lista de produse (functia searchProduct intoarce o refrinta nula), acesta
        este adaugat in lista
         */
        products.add(product);
    }

    /**
     * Metoda cauta un produs in lista de produse ale magazinului, identificat unic prin unique id-ul sau
     * @param uid unique id-ul produsului cautat
     * @return  referinta catre acel produs, daca este gasit in lista de produse, sau null, in daca produsul cautat nu
     * este gasit
     */
    public Product searchProduct (String uid) {
        for (Product p : products) {
            /*
            Daca s-a gasit un produs cu un unique id egal cu cel primit ca parametru, se intoarce referinta catre acel
            obiect
             */
            if (p.getUniqueId().equals(uid)) {
                return p;
            }
        }
        /*
        Altfel, se intoarce null
         */
        return null;
    }

    /**
     * Metoda creeaza o lista cu produsele dintr-un magazin produse de un anumit producator, primit ca parametru
     * @param manufacturer producatorul cautat
     * @return lista de produse din magazin produse de producatorul cautat
     */
    public ArrayList<Product> getProductsByManufacturer(Manufacturer manufacturer){
        /*
        Se initializeaza o lista de produse
         */
        ArrayList<Product> productsByManufacturer = new ArrayList<>();
        /*
        Pentru fiecare produs se verifica daca producatorul este cel primit ca parametru
         */
        for (Product p : products) {
            if (p.getManufacturer().equals(manufacturer)){
                /*
                Daca produsul este produs de producatorul primit ca parametru, produsul este adaugat in lista de produse
                 */
                productsByManufacturer.add(p);
            }
        }
        /*
        Se intoarce lista de produse
         */
        return productsByManufacturer;
    }

    /**
     * Metoda cauta o lista de produse in produsele magazinului si le calculeaza totalul
     * @param productsId lisat de unique id-uri ale produselor cautate
     * @return totalul produselor
     */
    public double calculateTotal(String[] productsId) {
        double total = 0;
        /*
        Fiecare produs este cautat in lista de produse folosind metoda searchProduct din clasa Store
         */
        for (String uid : productsId) {
            Product product = searchProduct(uid);
            if (product != null)
                /*
                Daca produsul a fost gasit, pretul acestuia este adaugat la total
                 */
                total += product.getPrice();
        }
        /*
        Se intoarce totalul produselor
         */
        return total;
    }

    /* DISCOUNTS */

    /**
     * Metoda creeaza un discount, ale carui informatii sunt primite ca parametri
     * @param discountType tipul discountului
     * @param value valoarea discountului
     * @param name denumirea discountului
     * @return discountul nou creat
     */
    public Discount createDiscount (DiscountType discountType, double value, String name) {
        /*
        Se creeaza un nou discount, se adauga in lista de disocunturi ale magazinului si se intoarce referinta la acesta
         */
        Discount discount = new Discount(name, discountType, value);
        discounts.add(discount);
        return discount;
    }

    /**
     * Metoda cauta un discount in lista de discounturi ale magazinului
     * @param discountType tipul discountului cautat
     * @param value valoarea discountului cautat
     * @return discountul cautat
     */
    public Discount searchDiscount (DiscountType discountType, double value) {
        /*
        Pentru fiecare discount din lista de discounturi ale magazinului, se verifica daca tipul si valoarea este agala
        cu cele introduse ca parametri
         */
        for (Discount d : discounts) {
            if (d.getDiscountType() == discountType && d.getValue() == value) {
                /*
                Daca discountul a fost gasit, se intoarce referinta catre acesta
                 */
                return d;
            }
        }
        /*
        Altfel, un nou discount cu tipul si valoarea primite este adaugat in lista de discounturi ale magazinului,
        cu ajutorul metodei createDiscount
         */
        return this.createDiscount(discountType, value, "");
    }

    /**
     * Metoda aplica un anumit discount produselor din magazin
     * @param discountType tipul discountului
     * @param value valoarea discountului
     * @throws NegativePriceException daca atunci cand se doreste aplicarea discountului unui sau mai multor produse
     * pretul ar fi negativ, este intoarsa aceasta exceptie
     */
    public void applyDiscount(DiscountType discountType, double value) throws NegativePriceException{
        /*
        Se cauta discountul in lista de disocunturi ale magazinului folosind metoda searchDiscount din clasa Store si
        este apelata metoda setAsAppliedNow din clasa Discount pentru a se marca discountul ca fiind aplicat
         */
        Discount discount = searchDiscount(discountType, value);
        discount.setAsAppliedNow();
        /*
        Variabila exceptionWasFound este folosita pentru a verifica daca cel putin un produs din lista de produse ar
        avea un pret negativ prin aplicarea discountului
         */
        boolean exceptionWasFound = false;

        /*
        Se parcurge lista de produse ale magazinului
         */
        for (Product p : products) {
            if (p.getDiscount() != null) {
                /*
                Daca un produs avea deja aplicat un discount, se revine la pretul initial al acestuia
                 */
                double oldPrice;
                if (p.getDiscount().getDiscountType() == DiscountType.FIXED_DISCOUNT) {
                    oldPrice = p.getPrice() + p.getDiscount().getValue();
                } else {
                    oldPrice = (p.getPrice() * 100) / (100 - p.getDiscount().getValue());
                }
                p.setPrice(oldPrice);
            }

            /*
            Se calculeaza noul pret al produsului, cu discountul curent
             */
            double price;
            if (discount.getDiscountType() == DiscountType.FIXED_DISCOUNT) {
                price = p.getPrice() - discount.getValue();
            } else {
                price = p.getPrice() * (100 - discount.getValue()) / 100;
            }

            if (price < 0) {
                /*
                Daca noul pret ar fi negativ, varibila exceptionWasFound este setata ca fiind true.
                Pretul produsului nu este schimbat, intrucat produsului nu ii este aplicat discountul.
                 */
                exceptionWasFound = true;
            } else {
                /*
                Altfel, daca pretul este in continuare pozitiv, se aplica discountul produsului: se seteaza discountul
                ca discountul din campul discount al produsului si se actualizeaza pretul acestuia
                 */
                p.setDiscount(discount);
                p.setPrice(price);
            }
        }

        /*
        Daca unul sau mai multe produse ar fi putut avea un pret negativ prin aplicarea discountului, este aruncata
        o exceptie de tipul NegativeProceException
         */
        if (exceptionWasFound)
            throw new NegativePriceException();
    }

    /* CSV */

    /**
     * Metoda citeste informatiile despre lista de produse ale unnui magazin, le prelucreaza si le adauga in obiectul
     * de tipul store
     * @param fileName numele fisierului CSV cu date de intrare
     * @return lista de produse ale magazinului
     * @throws IOException daca a aparut o eroare la citirea fisierului de input, este aruncata aceasta exceptie
     */
    public ArrayList<Product> readCSV(String fileName)  throws IOException {
        /*
        Se transforma fisierul CSV intr-o lista de intrari/linii care contin informatiile despre produse, ignorandu-se
        prima linie a fisierului, care reprezinta denumirile coloanelor
         */
        List<CSVRecord> records = CSVFormat.DEFAULT
                .withFirstRecordAsHeader()
                .parse(new FileReader(fileName))
                .getRecords();

        /*
        Se interpreteaza fiecare linie (record) a fisierului
         */
        for (CSVRecord record : records) {
            /*
            Se extrage pretul produsului, prezent pe a patra coloana a fisierului
             */
            String priceString = record.get(3);
            double price;
            if (priceString.isEmpty()) {
                /*
                Daca produsul nu are campul "price" completat, acesta este ignorat si se trece la urmatoarea linie a
                fisierului
                 */
                continue;
            } else {
                /*
                Se sterg caracterele "," din Stringul de pret
                 */
                priceString = priceString.replace(",", "");
                /*
                Se extrage simbolul monedei in care este dat pretul
                 */
                String symbol = priceString.substring(0, 1);
                /*
                Se cauta moneda dupa simbol in lista de monede ale magazinului
                 */
                Currency currency = this.searchCurrencyBySymbol(symbol);
                /*
                Se afla valoarea pretului in moneda curenta din magazin, impartindu-se pretul transformat in double la
                paritatea monedei curente si inmultindu-se la paritatea monedei in care este scris pretul in fisier
                 */
                price = Double.parseDouble(priceString.substring(1))  / currentCurrency.getParityToEur() * currency.getParityToEur();
            }

            /*
            Se initializeaza o variabila care va memora producatorul produsului curent
             */
            Manufacturer currentManufacturer;
            /*
            Se extrage denumirea producatorului, memorata in cea de a traia coloana a fisierului CSV.
            Daca denumirea este vida, se creeaza un producator cu denumirea "Not Available", altfel, se creeaza un
            producator cu denumirea din fisier.
             */
            String manufacturerName = record.get(2);
            if (manufacturerName.isEmpty()){
                currentManufacturer = new Manufacturer("Not Available");
            } else {
                currentManufacturer = new Manufacturer(manufacturerName);
            }
            /*
            Se adauga producatorul in lista de producatori ai magazinului, folosind metoda addManufacturer.
            Daca metoda s-a executat fara sa intoarca exceptia DuplicateManufacturerException, producatorul curent este
            unul nou, asa ca referinta stocata in currentManufacturer este cea din lista de producatori ai magazinului.
             */
            try {
                addManufacturer(currentManufacturer);
            } catch (DuplicateManufacturerException exception) {
                /*
                Daca producatorul produslui curent a fost introdus deja in lista de producatori, acesta este cautat in
                lista de producatori, iar variabila currentManufacturer va avea referinta acestuia din lista de
                producatori.
                 */
                currentManufacturer = searchManufacturer(currentManufacturer);
            }
            currentManufacturer.newProductAdded();

            /*
            Se extrag uniqu id-ul, denumirea si numarul din stoc ale produsului curent, care reprezinta prima, a doua,
            respectiv a cincea coloana din fisierul CSV
             */
            String uid = record.get(0);
            String name = record.get(1);
            /*
            Pentru numarul din stoc se elimina ultimele 4 caractere ale intrarii din tabel (non-breaking space si sirul
            "NEW") si se converteste numarul ramas la tipul int
             */
            String numAvailableString = record.get(4);
            numAvailableString = numAvailableString.substring(0, numAvailableString.length() - 4);
            int quantity = Integer.parseInt(numAvailableString);

            /*
            Se creeaza un nou produs folosinf clasa ProductBuilder cu datele extrase anterior din fisierul CSV
             */
            Product newProduct = new ProductBuilder()
                    .withUniqueId(uid)
                    .withName(name)
                    .withManufacturer(currentManufacturer)
                    .withPrice(price)
                    .withQuantity(quantity)
                    .withDiscount(null)
                    .build();
            /*
            Se adauga produsul in lista de produse ale magazinului, daca acesta nu exista deja in lista
             */
            try {
                addProduct(newProduct);
            } catch (DuplicateProductException ignored){
                /*
                Daca produsul exista deja in lista, exceptia DuplicateProductException va fi prinsa. In acest caz,
                produsul nu a mai fost adaugat inca o data in lista de produse.
                 */
            }
        }

        /*
        Se ordoneaza in ordine alfabetica lista de producatori
         */
        Collections.sort(manufacturers);
        /*
        Se intoarce lista de produse ale magazinului
         */
        return products;
    }

    /**
     * Metoda creeaza un nou fisier CSV cu numele primit ca parametru, in care se memoreaza informatiile despre
     * produsele magazinului in starea curenta
     * @param fileName numele fisierului care trebuie creat
     * @throws IOException daca a aparut o eroare la crearea fisierului, aceasta exceprie este aruncata
     */
    public void saveCSV(String fileName) throws IOException{
        /*
        Se creeaza un nou fisier CSV cu numele primit ca parametru, se adauga antetul fisierului si se specifica
        delimitatorul de coloane ale fisierului
         */
        FileWriter output = new FileWriter(fileName);
        CSVPrinter printer = new CSVPrinter(output, CSVFormat.DEFAULT
                .withHeader("uniq_id", "product_name", "manufacturer", "price", "number_available_in_stock")
                .withDelimiter(','));

        /*
        Se parcurge lista de produse ale magazinului si se adauga informatiile despre produse, in formatul cerut
         */
        for(Product p : products) {
            printer.printRecord(
                    p.getUniqueId(),
                    p.getName(),
                    p.getManufacturer().getName(),
                    currentCurrency.getSymbol() + p.getPrice(),
                    p.getQuantity() + "\u00A0NEW");
        }
    }
}