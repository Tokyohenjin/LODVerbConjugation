# LODVerbConjugation
Verb conjugation script using LOD API (https://lod.lu/api/doc)

The script takes a simple list as an input file (see provided sample). The list must fulfill the following criteria:

* No heading
* TXT file
* List of Luxembourgish verbs in the infinitive form
* All lower-case

The script then parses the list and searches LOD for the appropriate article ID. Simple checking is implemented to avoid issues with variants. In case this produces a parsing error, the script will prompt the user to input the correct ID. See the verb ‘kréien’ for an example of this behavior.
