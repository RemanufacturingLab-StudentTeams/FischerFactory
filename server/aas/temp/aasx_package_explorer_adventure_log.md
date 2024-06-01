log of what different versions of AASX Package Explorer do to an AASX file that a AAS server from Docker image v1.5.0 is trying to read.

> The only Dockerized examples for Basyx Databridge that I can find are from the basyx-java-examples repo. [This commmit](https://github.com/eclipse-basyx/basyx-java-examples/commit/8b1404ebef1da375f1acd1e561ed850ace6621b7) was the last one there, on Jul 3, 2023. Assuming Frank Schnicke, who made that commit, used the latest version of AASX Package Explorer then, it should be version `2023-02-03.alpha`.

AASX Package Explorer Version | Effect | Exception
| - | - | - |
2023-02-03.alpha | Corrupts the file format | `Exception in thread "main" org.apache.poi.openxml4j.exceptions.NotOfficeXmlFileException: No valid entries or contents found, this is not a valid OOXML (Office Open XML) file`
2024-02-27.alpha (LTS) | Converts file to V3, making it unreadable for the server | `[main] ERROR org.eclipse.basyx.components.aas.AASServerComponent -- Could not load initial AAS from source '/usr/share/config/updatertest.aasx'`
2022-05-10.alpha | Works! But it does use a very very outdated version of AAS... not great for inter-company exposition. | 
2022-08-06 | Works also, and is slightly less outdated.
2023-02-03.alpha | OH NOW THIS ONE WORKS TOO, *WHAT*
