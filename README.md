AdvancedFileSearchApp is a Kivy and KivyMD-based Python application that provides an advanced file search tool. The app allows users to search for files by their name and content across various file types such as .txt, .pdf, .docx, and .xlsx. The app features a responsive UI, progress indicators, and search result caching for faster subsequent searches.
Features

    File Name Search: Search for files by their names across directories.
    File Content Search: Search within the content of supported file formats (.txt, .pdf, .docx, .xlsx).
    Progress Indicators: Displays real-time progress of the search process.
    Search Result Caching: Stores previous search results for faster access.
    Pulsing UI Elements: Buttons and labels have pulsing animations for a dynamic look and feel.
    Stop Search Functionality: Allows the user to cancel a search mid-operation.
    Cross-Platform File Opening: Files can be opened using the default system application for the given platform (Windows, macOS, Linux).
    Tabbed Panel for Results: Displays search results in separate tabs for file name matches and content matches.

Components
1. GlowingLabel Class

A custom Label that has a glowing, pulsing animation.

Methods:

    __init__: Initializes the pulsing animation using Animation with alternating opacity.

2. PulseButton Class

A custom ButtonBehavior that uses an image as a button and grows in size when pressed.

Methods:

    __init__: Initializes the button with an image and pulsing animation.
    on_press: Starts the pulsing animation when the button is pressed.

3. AdvancedFileSearchApp Class

Main class for the file search application.

Attributes:

    stop_search_flag: A threading.Event to control when the search stops.
    search_thread: Holds the reference to the running search thread.
    search_cache: A dictionary to cache search results for future reuse.

UI Components:

    Search Bar: Includes a text input for the search keyword, a PulseButton for starting the search, and a Stop button for halting the search.
    Progress Bars: Two progress bars are used to display the search progress and file processing.
    Result Tabs: Displays search results in two tabs: one for files and one for content matches.

Methods:

    build: Constructs the UI and adds the components to the layout.
    _update_rect: Updates the background rectangle size and position when the window is resized.
    update_results: Populates the results from the file search and content search.
    update_progress: Updates the overall search progress.
    update_search_progress: Updates the search progress of individual files.
    update_results_count: Updates the label showing the number of results found.
    start_search: Initializes a new search in a separate thread and checks the cache for previous results.
    stop_searching: Stops the current search process.
    search_files: Searches through the filesystem for matching filenames and file content, then updates the UI.
    search_file_content: Reads files and checks if the search word is present within the file content.
    open_file: Opens the selected file using the system’s default application.

4. Search Progress

    Global Search Progress: The total progress for the entire search is displayed in a progress bar.
    Individual File Search Progress: Displays the progress of searching through each file.
    Result Count: Shows the total number of results found.

5. Supported File Types

The application can search inside the following file formats:

    .txt: Plain text files.
    .pdf: PDF documents (using the PyPDF2 library).
    .docx: Microsoft Word documents (using the python-docx library).
    .xlsx: Microsoft Excel files (using the openpyxl library).

6. Search Results

    File Tab: Displays files whose names match the search query.
    Content Tab: Displays files where the search query is found within the content.

Each result can be clicked to open the corresponding file using the system's default application.
7. Caching Mechanism

The application caches search results to improve performance for repeated searches. If the same keyword is searched again, the cached results are displayed instead of running a new search.
8. Threading

The search process runs in a separate thread to keep the UI responsive during long searches. The stop_search_flag event is used to stop the search process when needed.
9. Popup Notifications

Once a search is complete, a popup is shown to the user notifying them of the search completion.
How to Use

    Search: Enter a search keyword in the input field and click the search button (represented by an icon).
    Stop: If needed, the search can be stopped by clicking the "Stop Search" button.
    Results: View the results in two tabs: one for file matches and one for content matches.
    Open File: Click on any search result to open the file using the default application for that file type.
    Cache: Repeated searches with the same keyword will load results faster due to caching.

Dependencies

    Kivy
    KivyMD
    PyPDF2
    python-docx
    openpyxl

Conclusion

This application provides a comprehensive tool for advanced file searching, combining both file name and content searches across multiple file formats. It leverages Kivy for a responsive UI and threading for smooth, non-blocking operation.


#Apk-made-using-Google-Collab
https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbW1oSHluR1licE9YZFJybjE3T3VRTzNsTDBGUXxBQ3Jtc0tsUm5YbXpRci10V0ZfcWNoMllBaEJYemlxZEs2aGhWUTNVVzRZclJBWUNUV2J1Y0NxbWNXOWVKNnhtdEk4MzlsbHZkSEl2aEttdG8yNmlqMmRQYjZmTWN3ZTc5OWRYMV9xcFJXYWtRcjB3dGxjUnFOcw&q=https%3A%2F%2Fcolab.research.google.com%2Fdrive%2F1b9gMzs6XAtxCtahxei4N0fWZk7xiPlVw%3Fusp%3Dsharing&v=XqWLaMtDCyk
