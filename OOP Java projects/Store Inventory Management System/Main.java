import java.util.Scanner;

/**
 * Clasa Main contine metoda main executata la rulare.
 */
public class Main {
    /**
     * Metoda citeste comenzile si le interpreteaza, apeland comanda specifica pentru fiecare operatie ceruta
     */
    public static void main(String[] args){
        /*
        Se creeaza un magazin cu denumirea "POO ToyStore"
         */
        Store store = Store.Instance("POO ToyStore");

        /*
        Se creeaza un scanner pentru comenzile introduse
         */
        Scanner input = new Scanner(System.in);
        while (true) {
            /*
            Se citeste String-ul corespunzator comenzii introduse
             */
            String commandString = input.next();
            Command command = null;
            /*
            In functie de comanda introdusa de la tastatura, se determina ce comanda trebuie sa fie executata
             */
            switch (commandString) {
                case "loadcsv" -> command = new CommandLoadCSV(input);
                case "savecsv" -> command = new CommandSaveCSV(input);
                case "listcurrencies" -> command = new CommandListCurrencies();
                case "getstorecurrency" -> command = new CommandGetStoreCurrency();
                case "addcurrency" -> command = new CommandAddCurrency(input);
                case "setstorecurrency" -> command = new CommandSetStoreCurrency(input);
                case "updateparity" -> command = new CommandUpdateParity(input);
                case "showproduct" -> command = new CommandShowProduct(input);
                case "listproducts" -> command = new CommandListProducts();
                case "listproductsbymanufacturer" -> command = new CommandListProductsByManufacturer(input);
                case "listmanufacturers" -> command = new CommandListManufacturers();
                case "listdiscounts" -> command = new CommandListDiscounts();
                case "addiscount" -> command = new CommandAddDiscount(input);
                case "applydiscount" -> command = new CommandApplyDiscount(input);
                case "calculatetotal" -> command = new CommandCalculateTotal(input);
                /*
                Daca se introduce comanda "exit" sau "quit", executia programului este oprita
                 */
                default -> System.exit(0);
            }
            /*
            In cazul in care s-a introdus o comanda diferita de "exit" sau "quit", aceasta este executata
             */
            command.execute(store);
        }
    }
}