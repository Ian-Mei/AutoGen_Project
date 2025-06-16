/**
 * Lists the top-level folders in the user's Drive.
 */
function listRootFolders() {
  const query = '"root" in parents and trashed = false and ' +
    'mimeType = "application/vnd.google-apps.folder"';
  let folders;
  let pageToken = null;
  do {
    try {
      folders = Drive.Files.list({
        q: query,
        pageSize: 100,
        pageToken: pageToken
      });
      if (!folders.files || folders.files.length === 0) {
        console.log('All folders found.');
        return;
      }
      for (const folder of folders.files) {
        if (folder.name === '2025-2026 TCSA') {
          listFilesInFolder(folder.id);
        }
        console.log('%s (ID: %s)', folder.name, folder.id);
      }
      pageToken = folders.nextPageToken;
    } catch (err) {
      // TODO (developer) - Handle exception
      console.log('Failed with error %s', err.message);
    }
  } while (pageToken);
}


function listFilesInFolder(folderId) {
  var folder = Drive.getFolderById(folderId);
  var files = folder.getFiles();
  while (files.hasNext()) {
    var file = files.next();
    Logger.log(file.getName());
  }
}