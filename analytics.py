from sklearn.feature_extraction.text import CountVectorizer

# Calculate the ngram containment for one answer file/source file pair in a df
def calculate_containment(df, n, answer_filename):
    '''Calculates the containment between a given answer text and its associated source text.
       This function creates a count of ngrams (of a size, n) for each text file in our data.
       Then calculates the containment by finding the ngram count for a given answer text, 
       and its associated source text, and calculating the normalized intersection of those counts.
       :param df: A dataframe with columns,
           'File', 'Task', 'Category', 'Class', 'Text', and 'Datatype'
       :param n: An integer that defines the ngram size
       :param answer_filename: A filename for an answer text in the df, ex. 'g0pB_taskd.txt'
       :return: A single containment value that represents the similarity
           between an answer text and its source text.
    '''
    
    # your code here
    a_text = df[df['File'] == answer_filename]['Text'].values[0]
    orig_file = 'orig_task'+answer_filename[-5]+'.txt'
    s_text = df[df['File'] == orig_file]['Text'].values[0]
    
    counts = CountVectorizer(analyzer='word', ngram_range=(n,n))
    ngrams = counts.fit_transform([a_text, s_text])
    ngram_array = ngrams.toarray()
    
    a_text0 = np.array(ngram_array[0])
    s_text0 = np.array(ngram_array[1])
    
    inter = np.sum(min(a_s) for a_s in list(zip(ngram_array[0].tolist(), ngram_array[1].tolist())))
    return inter / np.sum(a_text0)
	

# Compute the normalized LCS given an answer text and a source text
def lcs_norm_word(answer_text, source_text):
    '''Computes the longest common subsequence of words in two texts; returns a normalized value.
       :param answer_text: The pre-processed text for an answer text
       :param source_text: The pre-processed text for an answer's associated source text
       :return: A normalized LCS value'''
    
    # your code here
    a_list = answer_text.split()
    s_list = source_text.split()
    
    init_mat = np.zeros((len(s_list)+1, len(a_list)+1))
    for i in range(1, len(s_list)+1):
        for j in range(1, len(a_list)+1):
            if s_list[i-1] == a_list[j-1]: # diagonal addition
                
                init_mat[i,j] = init_mat[i-1,j-1] + 1
            else: # max of top/left values
                init_mat[i,j] = max(init_mat[i,j-1], init_mat[i-1,j])
                
    
    return init_mat[-1,-1] / len(a_list)