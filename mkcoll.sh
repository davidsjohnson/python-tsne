marsyas-0.5.0/bin/mkcollection -l 0 genres/blues -c blues.mf
marsyas-0.5.0/bin/mkcollection -l 1 genres/classical -c classical.mf
marsyas-0.5.0/bin/mkcollection -l 2 genres/country -c country.mf
marsyas-0.5.0/bin/mkcollection -l 3 genres/disco -c disco.mf
marsyas-0.5.0/bin/mkcollection -l 4 genres/hiphop -c hiphop.mf
marsyas-0.5.0/bin/mkcollection -l 5 genres/jazz -c jazz.mf
marsyas-0.5.0/bin/mkcollection -l 6 genres/metal -c metal.mf
marsyas-0.5.0/bin/mkcollection -l 7 genres/pop -c pop.mf
marsyas-0.5.0/bin/mkcollection -l 8 genres/reggae -c reggae.mf
marsyas-0.5.0/bin/mkcollection -l 9 genres/rock -c rock.mf

marsyas-0.5.0/bin/bextract -sv blues.mf classical.mf country.mf disco.mf hiphop.mf jazz.mf metal.mf pop.mf reggae.mf rock.mf -w genres.arff -timbral

mv MARSYAS_EMPTYgenres.arff genres.arff
