import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.atomic.AtomicInteger;

public class ReduceTask implements Runnable{
    private final MyFile file;          // reduce task file
    private final ExecutorService tpe;
    private final AtomicInteger inQueue;

    public ReduceTask(MyFile file, ExecutorService tpe, AtomicInteger inQueue) {
        this.file = file;
        this.tpe = tpe;
        this.inQueue = inQueue;
    }

    @Override
    public void run() {
        int maxLen = 0;
        file.globalMaxWords = new ArrayList<>();

        // For every section's map
        for (int i = 0; i < file.maps.length; i++) {
            HashMap map = file.maps[i];
            // If map is not empty (section was not empty)
            if (!map.isEmpty()) {
                // Merge the section map in the final dictionary
                map.forEach(
                        (key, value) -> {
                            file.globalDictionary.merge((Integer) key, (Integer) value, Integer::sum);
                        }
                );

                // If section's max word length is greater than current final max word length
                if (file.maxWords[i].get(0).length() > maxLen) {
                    // Update max word length and final max words list
                    maxLen = file.maxWords[i].get(0).length();
                    file.globalMaxWords.clear();
                    file.globalMaxWords.addAll(file.maxWords[i]);
                }
                // If section's max word length equals the current final max word length
                else if (file.maxWords[i].get(0).length() == maxLen) {
                    // Add all max words from section to the final max words list
                    file.globalMaxWords.addAll(file.maxWords[i]);
                }

                // Clear the section map and max words list
                map.clear();
                file.maxWords[i].clear();
            }
        }

        // Remove 0 key
        file.globalDictionary.remove(0);

        // Compute the total number of words in the file
        int numOfWords = 0;
        for (Integer value : file.globalDictionary.values()) {
            numOfWords += value;
        }

        // Compute the sum
        Long sum = 0L;
        for (Map.Entry<Integer, Integer> entry : file.globalDictionary.entrySet()) {
            sum += (long) fib(entry.getKey() + 1) * entry.getValue();
        }

        // Compute the rank of file
        file.rank = (double) sum / numOfWords;

        // Make a release on the semaphore to mark that the reduce task has been completed
        Tema2.semaphore.release();

        int left = inQueue.decrementAndGet();
        if (left == 0) {
            tpe.shutdown();
        }
    }

    private Integer fib (int n) {
        if (n == 2)
            return 1;
        if (n == 3)
            return 2;

        int a = 1, b = 2, aux;
        for (int i = 4; i <= n; i++) {
            aux = a;
            a = b;
            b = a + aux;
        }
        return b;
    }
}
