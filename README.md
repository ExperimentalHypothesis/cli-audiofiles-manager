# CLI Audiofile Manager
Command line interface for managing audiofiles and folders. 

Personal microframework for managing audio files and audio folders. It started as a side project for online radio where the need for normalized audio files, properly tagged song and properly renamed fies or folders was a must.

It operates on filesystem with this tree structure:
```
<root>
  +---<artist name>
  |   +---<album name>
  |   |       <song name>
  |   |       <song name>
  |   |       <...>
  |   +---<album name>
  |   |       <song name>
  |   |       <song name>
  |   |       <...>
  +---<artist name>
  |   +---<album name>
  |   |       <song name>
  |   |       <song name>
  |   |       <...>
  |   +---<album name>
  |   |       <song name>
  |   |       <song name>
  |   |       <...>
  ```
There is only one root, that can contain mulitple artist folder, in each artist folder there can be multiple albums folders (since each artist can have number of releases), in each album folder, there can be multiple files (song files).

 
