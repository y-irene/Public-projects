import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class Tema2 {
    private static int workersNum;
    static long fragmentSize;
    private static long documentsNum;
    public static MyFile[] files;
    public static Semaphore semaphore;

    public static void main(String[] args) {
        try {
            if (args.length < 3) {
                System.err.println("Usage: Tema2 <workers> <in_file> <out_file>");
                return;
            }

            // Get input
            workersNum = Integer.parseInt(args[0]);

            File inFile = new File(args[1]);
            Scanner sc = new Scanner(inFile);
            fragmentSize = sc.nextLong();
            documentsNum = sc.nextLong();
            sc.nextLine();
            files = new MyFile[(int) documentsNum];
            for (int i = 0; i < documentsNum; i++) {
                String documentName = sc.nextLine();
                long fileSize = Files.size(Paths.get(documentName));
                long fragmentsNum = (long) Math.ceil((double) fileSize / fragmentSize);
                files[i] = new MyFile(i, documentName, fileSize, fragmentsNum, fragmentSize);
            }

            // MAP part
            // Initialize semaphore for map part
            int sections = 0;
            for (int i = 0; i < documentsNum; i++) {
                sections += files[i].fragmentsNum;
            }
            semaphore = new Semaphore(-sections + 1);

            // Add map tasks to task pool
            AtomicInteger inQueueMap = new AtomicInteger(0);
            ExecutorService mapTpe = Executors.newFixedThreadPool(workersNum);
            for (int i = 0; i < documentsNum; i++) {
                for (int j = 0; j < files[i].fragmentsNum; j++) {
                    inQueueMap.incrementAndGet();
                    mapTpe.submit(new MapTask(files[i], j, j * fragmentSize, mapTpe, inQueueMap));
                }
            }

            // This will succeed when all map tasks will have been completed
            semaphore.acquire();

            // REDUCE part
            // Initialize semaphore for reduce part
            semaphore = new Semaphore((int) (-documentsNum + 1));

            // Add reduce tasks to task pool
            AtomicInteger inQueueReduce = new AtomicInteger(0);
            ExecutorService reduceTpe = Executors.newFixedThreadPool(workersNum);
            for (int i = 0; i < documentsNum; i++) {
                inQueueReduce.incrementAndGet();
                reduceTpe.submit(new ReduceTask(files[i], reduceTpe, inQueueReduce));
            }

            // This will succeed when all reduce tasks will have been completed
            semaphore.acquire();

            // Sort file list by rank
            ArrayList<MyFile> filesList = new ArrayList<>(Arrays.asList(files));
            Collections.sort(filesList);

            FileWriter fileWriter = new FileWriter(args[2]);
            PrintWriter printWriter = new PrintWriter(fileWriter);

            // For every file in list
            for (MyFile file : filesList) {
                StringBuilder sb = new StringBuilder();
                // Get file name from path
                String[] filePath = file.name.split("/");
                // Create file line for output file
                sb.append(filePath[filePath.length - 1] + ",")
                        .append(String.format("%.2f", file.rank) + ",")
                        .append(file.globalMaxWords.get(0).length()).append(",")
                        .append(file.globalMaxWords.size() + "\n");
                // Add line in output file
                printWriter.print(sb);
            }
            printWriter.close();
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
}
