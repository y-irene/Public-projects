import java.io.IOException;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Scanner;

/**
 * Clasa abstracta Command implementeaza design pattern-ul Command
 */
public abstract class Command {
    /**
     * Medota abstracta prin care se efectueaza operatiile corespunzatoare diferitelor comenzi
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public abstract void execute(Store store);
}

/**
 * Clasa CommandLoadCSV extinde clasa Command si implementeaza comanda de tipul "loadstore". Aceasta comanda
 * presupune citirea datelor despre produsele unui magazin dintr-un fisier CSV si memorarea acestora
 * in obiectul de tip Store corespunzator
 */
class CommandLoadCSV extends Command {
    /**
     * Constanta de tip Scanner cu ajutorul careia se citesc datele de intrare necesare pentru realizarea comenzii
     */
    private final Scanner input;

    /**
     * Constructor cu parametri
     * @param input Scanner folosit pentru a citi restul de date necesare comenzii (denumirea fisierului de input)
     */
    public CommandLoadCSV(Scanner input) {
        this.input = input;
    }

    /**
     * Metoda (suprascrisa din clasa parinte  abstracta) realizeaza operatiile necesare pentru realizarea comenzii
     * "loadstore"
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store){
        /*
        Se citeste de la tastatura numele fisierului de input.
         */
        String fileName = input.next();
        try {
            /*
            Se apeleaza metoda readCSV care citeste datele din fisierul CSV.
            Daca a aparut o problema la citirea din fisier, o exceptie de tipul IOException este aruncata.
             */
            store.readCSV(fileName);
        } catch (IOException e){
            /*
            Daca a fost aruncata o exceptie de tipul IOExcepton, acesta este prinsa si se va afisa mesajul "Cannot read
            input from [fileName] file". In acest caz, datele de intrare nu au fost citite cu succes, asa ca executia
            programului este intrerupta si se intoarce exit code-ul 1.
             */
            System.out.println("\tCannot read input from " + fileName + " file");
            System.exit(1);
        }
    }
}

/**
 * Clasa CommandSaveCSV extinde clasa Command si implementeaza comanda de tip "savestore". Aceasta metoda presupune
 * scrierea datelor despre produsele curente ale unnui obiect de tipul Store intr-un fisier CSV
 */
class CommandSaveCSV extends Command {
    /**
     * Constanta de tip Scanner cu ajutorul careia se citesc datele de intrare necesare pentru realizarea comenzii
     */
    private final Scanner input;

    /**
     * Constructor cu parametri
     * @param input Scanner folosit pentru a citi restul de date necesare comenzii (denumirea fisierului de output)
     */
    public CommandSaveCSV(Scanner input) {
        this.input = input;
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) realizeaza operatiile necesare pentru realizarea comenzii
     * "savestore"
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store){
        /*
        Se citeste de la tastatura numele fisierului de output.
         */
        String fileName = input.next();
        try {
            /*
            Se apeleaza metoda saveCSV care creeaza un fisier CSV cu datele despre produsele curent din store.
            Daca a aparut o problema la crearea fisierului, o exceptie de tipul IOException este aruncata.
             */
            store.saveCSV(fileName);
        } catch (IOException e){
            /*
            Daca a fost aruncata o exceptie de tipul IOExcepton, acesta este prinsa si se va afisa mesajul "Cannot write
            output in [fileName] file". In acest caz, salvarea datelor despre produse nu s-a efetuat cu succes.
             */
            System.out.println("\tCannot write output in" + fileName + "file");
        }
    }
}

/**
 * Clasa CommandListCurrencies extinde clasa Command si implementeaza comanda de tip "listcurrencies".
 * Aceasta comanda presupune afisarea monedelor care pot fi folosite la momentul curent de un obiect de tipul Store.
 */
class CommandListCurrencies extends Command {
    /**
     * Constructor fara parametri
     */
    public CommandListCurrencies() {
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) afiseaza monedele care pot fi folosie la momentul curent de
     * obiectul de tip Store primit ca parametru
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store) {
        /*
        Pentru fiecare element din ArrayList-ul de monede din obiectul store se afiseaza denumirea si paritatea la EUR,
        concatenate si despartite printr-un spatiu.
         */
        for (Currency c : store.getCurrencies()) {
            System.out.println("\t" + c.getName() + " " + c.getParityToEur());
        }
    }
}

/**
 * Clasa CommandGetStoreCurrency extinde clasa Command si implementeaza comanda de tip "getstorecurrency".
 * Aceasta comanda presupune afisarea monedei curente in care sunt retinute preturile produselor dintr-un obiect de
 * tipul Store.
 */
class CommandGetStoreCurrency extends Command {
    /**
     * Constructor fara parametri
     */
    public CommandGetStoreCurrency() {
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) afiseaza numele monedei curente utilizate de obiectul de tip
     * Store primit ca parametru
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store) {
        /*
        Se apeleaza getter-ul pentru moneda curenta a magazinului si se afiseaza denumirea acesteia
         */
        Currency storeCurrency = store.getCurrentCurrency();
        System.out.println("\t" + storeCurrency);
    }
}

/**
 * Clasa CommandAddCurrency extinde clasa Command si implementeaza comanda de tip "addcurrency".
 * Aceasta comanda presupune citirea de la tastatura a datelor unei noi monede si adaugarea acesteia in lista de monede
 * ale unui obiect de tipul Store.
 */
class CommandAddCurrency extends Command {
    /**
     * Constanta de tip Scanner cu ajutorul careia se citesc restul datelor de intrare necesare realizarii comenzii
     */
    private final Scanner input;

    /**
     * Constructor cu parametri
     * @param input Scanner folosit pentru a citi restul de date necesare pentru realizarea comenzii (denumirea,
     *              simbolul si paritataea la euro a noii monede)
     */
    public CommandAddCurrency(Scanner input) {
        this.input = input;
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) citeste de la tastatura informatiile unei noi monede si le
     * adauga in lista de monede ale unui obiect de tipul Store
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store) {
        /*
        Se citesc de la tastatura denumirea, simbolul si paritatea fata de euro a noii monede
         */
        String name = input.next();
        String symbol = input.next();
        double parityToEuro = input.nextDouble();
        /*
        Se apeleaza metoda createCurrency, care va crea un nou obiect de tipul Currency si il va adauga in lista de monede ale obiectului store.
         */
        store.createCurrency(name, symbol, parityToEuro);
    }
}

/**
 * Clasa CommandSetStoreCurrency extinde clasa Command si implementeaza comanda de tip "setstorecurrency".
 * Aceasta comanda presupune schimbarea monedei curente cu alta din lista de monede ale unui obiect de tipul Store.
 */
class CommandSetStoreCurrency extends Command {
    /**
     * Constanta de tip Scanner cu ajutorul careia se citesc restul datelor de intrare de la tastatura
     */
    private final Scanner input;

    /**
     * Constructor cu parametri
     * @param input Scanner folosit pentru a citi restul de date necesare pentru realizarea comenzii (denumirea monedei
     *              care se doreste sa fie setata)
     */
    public CommandSetStoreCurrency(Scanner input) {
        this.input = input;
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) citeste de la tastatura denumirea unei monede, care va inlocui
     * moneda curenta a obiectului de tip Store, doar daca aceasta exista
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store) {
        /*
        Se citeste de la tastatura denumirea monedei cautate si se creeaza o moneda temporara cu acea denumire
         */
        String currencyName = input.next();
        Currency temporaryCurrency = new Currency();
        temporaryCurrency.setName(currencyName);
        try {
            /*
            Se apeleaza metoda changeCurrency pentru a schimba moneda actuala cu cea care are aceeasi denumire cu cea
            temporara.Daca o moneda cu aceeasi denumire nu va fi gasita in lista de monede ale obiectului store, este
            aruncata o exceptie de tipul CurrencyNotFoundException.
             */
            store.changeCurrency(temporaryCurrency);
        } catch (CurrencyNotFoundException ignored) {
            /*
            Daca nu s-a gasit moneda cautata, exceptia de tipul CurrencyNotFoundException este prinsa in blocul catch.
            Aceasta nu influenteaza in mod major rularea programului, doar ca ,oneda curenta nu este actualizata,
            intrucat moneda cauta nu exista.
             */
        }
    }
}

/**
 * Clasa CommandUpdateParity extinde clasa Command si implementeaza comanda de tip "updateparity".
 * Aceasta comanda presupune citirea unei noi paritati pentru o anumita moneda din obiectul de tip Store si
 * actualizarea paritatii acesteia.
 */
class CommandUpdateParity extends Command {
    /**
     * Constanta de tip Scanner cu ajutorul careia se pot citi restul datelor de intrare
     */
    private final Scanner input;

    /**
     * Constructor cu parametri
     * @param input Scanner folosit pentru a citi restul de date necesare pentru realizarea comenzii
     *              (denumirea monedei si noua paritate)
     */
    public CommandUpdateParity(Scanner input) {
        this.input = input;
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) citeste de la tastatura denumirea unei monede si noua valoare a
     * paritatii si va actualiza paritatea monedei citite la valoarea introdusa
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store) {
        /*
        Se citesc denumirea si noua paritate a monedei de la input
         */
        String currencyName = input.next();
        double newParity = input.nextDouble();
        /*
        Se apeleaza metoda searchCurrencyByName din clasa Store pentru a se afla referinta catre moneda dorita.
         */
        Currency currencyToUpdate = store.searchCurrencyByName(currencyName);
        /*
        Daca moneda a fost gasita in lista de monede ale obiectului store, adica daca referinta catre aceasta este
        diferita de null, se apeleaza metoda updateParity din clasa Currency (setter pentru campul parityToEur al
        obiectului de tip Currency), care va modifica valoarea paritatii la noua paritate.
         */
        if (currencyToUpdate != null){
            currencyToUpdate.updateParity(newParity);
        }
    }
}

/**
 * Clasa CommandShowProduct extinde clasa Command si implementeaza comanda de tip "showproduct".
 * Aceasta presupune cautarea unui anumit produs in lista de produse ale unui magazin si afisarea informatiilor despre
 * acesta
 */
class CommandShowProduct extends Command {
    /**
     * Constanta de tip Scanner cu ajutorul careia se pot citi restul datelor de intrare de la tastatura
     */
    private final Scanner input;

    /**
     * Constructor cu parametri
     * @param input Scanner folosit pentru a citi restul de date necesare pentru realizarea comenzii (unique id-ul
     *              produsului care se doreste sa se afiseze)
     */
    public CommandShowProduct(Scanner input) {
        this.input = input;
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) citeste de la input unique id-ul unui produs si , daca este
     * gasit in lista de produse ale magazinului, afiseaza informatiile despre acesta
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store) {
        /*
        Se citeste unique id-ul produsului cautat
         */
        String uid = input.next();
        /*
        Se apeleaza metoda searchProduct din clasa Store care cauta un produs in lista de produse ale unui magazin si
        intoarce referinta catre acesta, daca este gasit, sau null, in caz contrar.
         */
        Product product = store.searchProduct(uid);
        /*
        Daca produsul a fost gasit in lista de produse ale magazinului (daca referinta catre acesta este diferita de
        null), informatiile despre acesta sunt afisate cu ajutorul metodei showProduct din clasa Product.
         */
        if (product != null) {
            product.showProduct(store.getCurrentCurrency());
        } else {
            System.out.println("\tProduct with unique id " + uid + " doesn't exist");
        }
    }
}

/**
 * Clasa CommandListProducts extinde clasa Command si implementeaza comanda de tip "listproducts".
 * Aceasta presupune afisarea informatiilor despre toate produsele stocate intr-un obiect de tipul Store.
 */
class CommandListProducts extends Command {
    /**
     * Constructor fara parametri
     */
    public CommandListProducts() {
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) si afiseaza informatiile despre toate produsele stocate in
     * magazin
      * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store) {
        /*
        Pentru fiecare produs din lista de produse ale magazinului se afiseaza informatiile despre acesta prin
        intermediul metodei showProduct din clasa Product
         */
        for (Product p : store.getProducts()){
            p.showProduct(store.getCurrentCurrency());
        }
    }
}

/**
 * Clasa CommandListProductsByManufacturer extinde clasa Command si implementeaza comanda de tip
 * "listproductsbymanufacturer". Aceasta presupune afisarea produselor produse de un anumit producator, al carui nume
 * este citit de la input
 */
class CommandListProductsByManufacturer extends Command {
    /**
     * Constanta de tip Scanner cu ajutorul careia se pot citi restul datelor de intrare necesare realizarii comenzii
     * (numele producatorului)
     */
    private final Scanner input;

    /**
     * Constructor cu parametri
     * @param input Scanner folosit pentru a citi restul de date necesare pentru realizarea comenzii ()
     */
    public CommandListProductsByManufacturer(Scanner input) {
        this.input = input;
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) citeste de la input numele unui producator si afiseaza produsele
     * stocate intr-un obiect de tip store care sunt produse de producatorul introdus.
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store) {
        /*
        Se citeste de la input numele producatorului cautat
         */
        String name = input.nextLine();
        name= name.substring(1);
        /*
        Se cauta referinta catre producatorul introdus in lista de producatori ai magazinului.
         */
        Manufacturer manufacturer = store.searchManufacturer(new Manufacturer(name));
        /*
        Se initializeaza o noua lista de produse in care sunt stocate referintele catre produsele produse de
        producatorul introdus la tastatura.
         */
        ArrayList<Product> productsByManufacturer = store.getProductsByManufacturer(manufacturer);
         /*
         Daca lista nu este vida, se afiseaza informatiile despre produsele gasite care au producatorul cautat cu
         ajutorul metodei showProduct din clasa Product.
          */
        if (!productsByManufacturer.isEmpty()) {
            for (Product p : productsByManufacturer){
                p.showProduct(store.getCurrentCurrency());
            }
        }
    }
}

/**
 * Clasa CommandListManufacturers extinde clasa Command si implementeaza comanda de tip "listmanufacturers".
 * Aceasta comanda presupune afisarea liste de producatori ai unui obiect de tipul Store.
 */
class CommandListManufacturers extends Command {
    /**
     * Constructor fara parametri
     */
    public CommandListManufacturers() {
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) afiseaza lista de producatori memorata in campul manufacturers
     * al obiectului store.
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store) {
        /*
        Pentru fiecare producator din lista de producatori se afiseaza numele.
         */
        for (Manufacturer m : store.getManufacturers()){
            System.out.println("\t" + m.getName());
        }
    }
}

/**
 * Clasa CommandListDiscounts extinde clasa Command si implementeaza comanda de tip "listdiscounts".
 * Aceasta comanda presupune afisarea informatiilor despre toate discounturile presente intr-un obiect de tipul Store.
 */
class CommandListDiscounts extends Command {
    /**
     * Constructor fara parametri
     */
    public CommandListDiscounts() {
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) afiseaza informatiile fiecarui discount din lista de
     * discounturi ale obiectului store.
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store) {
        /*
        Pentru fiecare discount din lista de discounturi ale obiectului store se afiseaza tipul, valoarea, numele si,
        daca este cazul, data la care a fost aplicat produselor.
         */
        for (Discount d : store.getDiscounts()) {
            System.out.print("\t" + d.getDiscountType() + " " + d.getValue() + " " + d.getName() + " ");
            if (d.getLastDateApplied() != null) {
                System.out.print(d.getLastDateApplied().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            }
            System.out.println();
        }
    }
}

/**
 * Clasa CommandAddDiscount extinde clasa Command si implementeaza comanda de tip "adddiscount".
 * Aceasta comanda presupune adaugarea unui discount, ale carui date sunt citite de la tastatura, in lista de
 * discounturi ale unui obiect de tipul Store.
 */
class CommandAddDiscount extends Command {
    /**
     * Constanta de tip Scanner cu ajutorul careia se citesc restul datelor de intrare de la tastatura
     * (tipul, valoarea si numele discountului)
     */
    private final Scanner input;

    /**
     * Constructor cu parametri
     * @param input Scanner folosit pentru a citi restul de date necesare pentru realizarea comenzii ()
     */
    public CommandAddDiscount(Scanner input) {
        this.input = input;
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) citeste de la tastatura informatiile despre un discount. Aceasta
     * creeaza un nou obiect de tipul Discount si il adauga in lista de discounturi ale obiectului store cu ajutorul
     * unei functii auxiliare.
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store) {
        /*
        Se citesc de la tastatura tipul discountului, valoarea si numele acestuia.
         */
        String typeString = input.next();
        DiscountType type;
        if (typeString.equals("PERCENTAGE"))
            type = DiscountType.PERCENTAGE_DISCOUNT;
        else
            type = DiscountType.FIXED_DISCOUNT;
        double value = input.nextDouble();
        String name = input.nextLine();
        /*
        Se creeaza un nou obiect de tipul Discount si se adauga in lista de discounturi ale obiectului store cu
        ajutorul metodei createDiscount din clasa Store.
         */
        store.createDiscount(type, value, name);
    }
}

/**
 * Clasa CommandApplyDiscount extinde clasa Command si implementeaza comanda de tip "applydiscount".
 * Aceasta comanda presupune aplicarea unui disocunt introdus de la tastatura asupra tuturor produselor stocate intr-un
 * obiect de tipul Store.
 */
class CommandApplyDiscount extends Command {
    /**
     * Constanta de tip Scanner cu ajutorul careia se citesc restul datelor de intrare necesare realizarii comenzii.
     */
    private final Scanner input;

    /**
     * Constructor cu parametri
     * @param input Scanner folosit pentru a citi restul de date necesare pentru realizarea comenzii ()
     */
    public CommandApplyDiscount(Scanner input) {
        this.input = input;
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) citeste de la tastatura datele unui discount si il aplica,
     * cu ajutorul metodei auxiliare applyDiscount din clasa Store, tuturor produselor unui obiect store
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store) {
       /*
       Se citesc de la tastatura tipul si valoarea unui disocunt.
        */
        String typeString = input.next();
        DiscountType type;
        if (typeString.equals("PERCENTAGE"))
            type = DiscountType.PERCENTAGE_DISCOUNT;
        else
            type = DiscountType.FIXED_DISCOUNT;
        double value = input.nextDouble();

        /*
        Se apeleaza metoda applyDiscount din clasa store, care va modifica preturile produselor, corespunzator
        discountului dat ca parametru prin tip si valoare.
         */
        try {
            store.applyDiscount(type, value);
        } catch (NegativePriceException ignored) {
            /*
            Daca atunci cand s-a aplicat discountul tuturor produsel, unul dintre ele ar fi avut un pret negativ prin
            aplicarea discountului, este aruncata o excectie de tipul NegativePriceException. Daca exceptia a fost
            aruncata inseamna ca nu toate produsele au aplicat discountul respectiv.
             */
        }
    }
}

/**
 * Clasa CommandCalculateTotal extinde clasa Command si implementeaza comanda de tip "calculatetotal".
 * Aceasta comanda presupune citirea de la tastatura a unique id-urilor mai multor produse si calcularea si afisarea
 * totalului acestora.
 */
class CommandCalculateTotal extends Command {
    /**
     * Constanta de tip Scanner cu ajutorul careia se pot citi restul datelor de intrare (unique id-urile produselor
     * cautate).
     */
    private final Scanner input;

    /**
     * Constructor cu parametri
     * @param input Scanner folosit pentru a citi restul de date necesare pentru realizarea comenzii ()
     */
    public CommandCalculateTotal(Scanner input) {
        this.input = input;
    }

    /**
     * Metoda (suprascrisa din clasa parinte abstracta) citeste unique id-urile mai multor produse si calculeaza
     * totalul acestora, afisandu-l.
     * @param store obiectul de tipul Store asupra caruia urmeaza sa se execute comanda
     */
    public void execute(Store store) {
        /*
        Se citesc unique id-urile produselor cautate, concatente, cu spatiu intre ele.
         */
        String line = input.nextLine();
        line = line.substring(1);
        /*
        String-ul este impartit dupa spatii, astfel rezultand un vector cu elemente de tipul String, care reprezinta
        exact unique id-urile fiecarui produs cautat.
         */
        String[] productsId = line.split(" ", 0);
        /*
        Se afiseaza simbolul monedei curente, impreuna cu rezultatul metodei calculateTotal din clasa Store.
         */
        System.out.println("\t" + store.getCurrentCurrency().getSymbol() + store.calculateTotal(productsId));
    }
}