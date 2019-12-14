HTML = '''
<h1>Purpose</h1>
  <p>This application helps you manage the migration of files from one file location to another, 
  including network shares.</p>
  <p>Typical scenario:
    <ol>
      <li>You have bunch of files in a bunch of directories on a shared drive. They've gotten old and disorganized.</li>
      <li>You create a new shared drive/directory and a new folder structure to better organize the files.</li>
      <li>People, over time, move files from the old location to the new location; 
        files may be renamed and placed in a different folder in the new location.</li>
      <li>Files in the new location may be updated after the "move".</li>
      <li>Eventually, the old location can be retired when the new location contains all 
        the relevant files with proper names and organization</li>
    </ol>
    What could go wrong?
  </p>
  <p>The typical problem in this scenario is that some files in the old location are stragglers; 
    they inadvertently fail to get copied to the new location. How do you find them?
  </p>
  <p>This program examines all the files in "old" and "new" locations and categorizes them a few ways:
    <ul>
      <li><em>Matched</em>: Files <u>match</u> when they have the same <u>contents</u> even though they may have different names.</li>
      <li><em>Unmatched</em>: A file is <u>unmatched</u> in the <u>old</u> location when there is no file with the 
      same contents in the <u>new</u> location.</li>
      <li><em>Updated</em>: A file with the same name exists in the <u>new</u> location but the old and new contents
        are different. <em>Note:</em> An <u>updated</u> file is also an <u>unmatched</u> file since the computer can't tell
        whether the file was simply moved and updated or whether there is another file with a conflicting name.
    </ul>
  </p>
<h1>Tips</h1>
  <p>Some quick points about using this application:
    <ol>
      <li>Set the options on the "Options" tab and click the <em>Start</em> button; the program will start scanning.</li>
      <li>When the scann is complete, use the other tabs to review the results</li>
      <li>Resize columns by dragging the separators between them.</li>
      <li>Click a column header to sort the rows in ascending order. Click again to sort in descending order.</li>
      <li>Drag a column header to re-order the columns</li>
      <li>Right-click a row for a popup menu to open one of the selected files.</li>
    </ol>
  </p>
<h2>Options Tab</h2>
  <p>Set scanning options and start or stop the scanning process.</p>
  <p>You can limit the number of files to be scanned. This would be helpful for checking that the results 
    are what you expect before scanning a huge number of files.</p>
  <p>The old and new directory locations are required. You can use the <em>Select</em> buttons to visually select a location.</p>
  <p>When the options are valid, the <em>Start</em> button is enabled. Click it to start scanning.</p>
  <p>If scanning is taking too long, you can click the <em>Stop</em> button.</p>
  <h2>Unmatched Tab</h2>
  <p>The <em>Unmatched</em> tab shows files in the old location that have no matching contents in the new location.</p>
  <p>A file that was copied (without changing its name) and subsequently modified will appear in this list. </p>
  <p>The <em>New Name Matches</em> column shows the count of files in the new location that have the same name but different contents.</p>
  <p><em>Tip:</em> Sort the <em>New Name Matches</em> column to focus on the non-zero rows.</p>
  <p><em>Tip:</em> Right-click a row to open the the old file</p>
  <h2>Matched Tab</h2>
  <p>Files on this tab have matches between the old and new location.
    A file matches only if its <em>contents</em> are the same even though its name and organization may have changed.
  </p>
  <p>The <em>Name Changed</em> column indicates whether the matching files have different names.</p>
<h2>Updated Tab</h2>
  <p>The <em>Updated</em> tab shows files that have the same names but different contents.</p>
  <p>An updated file should have a newer modification date than its older version.
    The <em>More Recent</em> column shows whether the new file is more recent than the olde file.
  </p>
  <p><em>Tip:</em> Sort the <em>More Recent</em> column to focus on files that are <em>not</em> 
    more recent. These are probably cases where files have the same name but are not otherwise related 
    to each other.</p>
  <p><em>Tip:</em> Use the popup menu for a row to open the new or old versions.</p>
<h2>Log Tab</h2>
  <p>The <em>Log</em> tab has some details about the programs operation that are normally
  only useful for troubleshooting.</p>
  <p><em>Tip:</em> The first entry in the log should identify the program version number.</p>
'''