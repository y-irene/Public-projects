import java.util.ArrayList;
import java.util.HashMap;

public class MyFile implements Comparable{
    public final int index;                 // file index in initial file list
    public final String name;               // file path
    public final long size;                 // file size
    public final long fragmentsNum;         // file fragments number
    public final long fragmentSize;         // file fragments number
    public HashMap<Integer, Integer>[] maps;// all sections maps array
    public ArrayList<String>[] maxWords;    // all sections max words array

    public HashMap<Integer, Integer> globalDictionary;  // final dictionary
    public ArrayList<String> globalMaxWords;            // final max word list
    public Double rank;                                 // file rank

    public MyFile(int index, String name, long size, long fragmentsNum, long fragmentSize) {
        this.index = index;
        this.name = name;
        this.size = size;
        this.fragmentsNum = fragmentsNum;
        this.fragmentSize = fragmentSize;
        maps = new HashMap[(int)fragmentsNum];
        maxWords = new ArrayList[(int)fragmentsNum];
        for (int i = 0; i < fragmentsNum; i++) {
            maps[i] = new HashMap<>();
        }
        globalDictionary = new HashMap<>();
    }

    @Override
    public int compareTo(Object o) {
        MyFile file = (MyFile)o;
        if (this.rank < file.rank)
            return 1;
        else if (this.rank > file.rank)
            return -1;
        else
            return 0;
    }
}
