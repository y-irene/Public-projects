import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.atomic.AtomicInteger;

public class MapTask implements Runnable {
    private final MyFile file;          // file of the map task
    private final int fileSectionId;    // section id in the file
    private final long offset;          // offset in the file
    private final ExecutorService tpe;
    private final AtomicInteger inQueue;
    private static String separators = " ;:/?~\\.,><`[]{}()!@#$%^&-_+'=*\"| \t\r\n\0";
    private static String regex = "[;|:|/|?|~|\\|.|,|>|<|'|\\[|\\]|{|}|(|)|!|@|#|$|%|^|&|\\-|_|+|=|*|\"| |\t|\r|\n]+";

    public MapTask(MyFile file, int fileSectionId, long offset, ExecutorService tpe, AtomicInteger inQueue) {
        this.file = file;
        this.fileSectionId = fileSectionId;
        this.offset = offset;
        this.tpe = tpe;
        this.inQueue = inQueue;
    }

    @Override
    public void run() {
        try {
            // Compute initial start and end of file section
            long start = offset;
            long end = Math.min(offset + file.fragmentSize, file.size);

            FileInputStream fileInputStream = new FileInputStream(file.name);
            StringBuilder sb = new StringBuilder();

            // Compute correct start
            if (start > 0) {
                // Skip the first (offset - 1) bytes
                fileInputStream.skip(offset - 1);
                start = offset - 1;

                // Check if letter before offset is separator
                char previousChar = (char)fileInputStream.read();
                start++;
                boolean previousCharIsSeparator = charIsSeparator(previousChar);

                // Check if letter at offset is separator
                char firstChar = (char)fileInputStream.read();
                start++;
                boolean firstCharIsSeparator = charIsSeparator(firstChar);

                boolean offsetMarksStartOfWord = previousCharIsSeparator || firstCharIsSeparator;

                // If offset does not mark the start of a word
                if (!offsetMarksStartOfWord) {
                    // Skip until you reach a separator
                    char current = (char)fileInputStream.read();
                    start++;
                    while (!charIsSeparator(current) && (start < end)) {
                        current = (char)fileInputStream.read();
                        start++;
                    }

                    // Skip until you reach start of word
                    while (charIsSeparator(current) && (start < end)) {
                        current = (char)fileInputStream.read();
                        start++;
                    }

                    // If last checked character is not a separator and not the section end,
                    // it is the first character of the word
                    if (!charIsSeparator(current) && (start != end)) {
                        sb.append(current);
                    }
                }
                // If offset marks start of word
                else {
                    sb.append(firstChar);
                }
            }

            // Add the characters from correct start and initial end in the string of the current section
            char lastChar = 0;
            for (int i = (int)start; i < (int)end; i++) {
                lastChar = (char)fileInputStream.read();
                sb.append(lastChar);
            }

            // Compute the correct end
            if ((end < file.size) && (start != end)) {
                char nextChar = (char)fileInputStream.read();
                // If the current end does not mark the end of the word, append the character to the current section string
                while (!charIsSeparator(lastChar) && !charIsSeparator(nextChar) && (end < file.size)) {
                    sb.append(nextChar);
                    lastChar = nextChar;
                    nextChar = (char)fileInputStream.read();
                    end++;
                }
            }

            // If the section is not empty
            String section = sb.toString();
            if (!section.isBlank()) {
                // Split section into words
                ArrayList<String> words = new ArrayList<>(Arrays.asList(section.split(regex)));

                // For every word in the section
                int maxLen = 0;
                ArrayList<String> maxWords = new ArrayList<>();
                for (String word : words) {
                    // Check its length
                    if (word.length() > maxLen) {
                        // If the length is greater than the current max length, update the max length and the max words list
                        maxLen = word.length();
                        maxWords.clear();
                        maxWords.add(word);
                    } else if (word.length() == maxLen) {
                        // If the length equals the current max length, add word to max words list
                        maxWords.add(word);
                    }
                    // If the word's length is new, add it to the section map
                    Integer ret = file.maps[fileSectionId].putIfAbsent(word.length(), 1);
                    if (ret != null) {
                        // Otherwise, increase the value at the length key by 1
                        file.maps[fileSectionId].put(word.length(), ret + 1);
                    }
                }

                // Add section's max words list to the max words array of the file
                file.maxWords[fileSectionId] = maxWords;
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        // Make a release on the semaphore to mark that the processing of the section is done
        Tema2.semaphore.release();

        int left = inQueue.decrementAndGet();
        if (left == 0) {
            tpe.shutdown();
        }
    }

    private static boolean charIsSeparator (char c) {
        return separators.contains(String.valueOf(c));
    }


}
