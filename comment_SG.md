# Commentaires au  28/03/2019

commit 6bba52b3f9e856549ef36b2222be5e6fca192d13

## main.py

```
directory = CaseDirectory("./Results")  # creation
world.set_directory(directory)  # registration
```

Est-ce que ta classe `CaseDirectory` a réellement une utilisé ? Ne serait-il pas plus simple d'insérer le contenu de sa méthode `create` directement dans `Wolrd` ?

De même, la méthode `adapt_path` ne peut-elle pas être remplacée par une fonction qui existe déjà nativement dans Pyhton ?

   
```
supervisor = Supervisor("glaDOS", "DummySupervisorMain.py")
supervisor.description = "this supervisor is a really basic one. It just serves as a " \
                         "skeleton/example for your (more) clever supervisor."
```

Je ne suis pas fan de passer la référence à un superviseur via une chaine de caractère qui contient le nom du fichier code source ! Pourquoi ne crées-tu pas simplement une instance de `DummySupervisorMain` (qui hérite de `Supervisor`) à ton `world` ?
  
Idem pourquoi tu utilises un attribut pour fixer la description ? Non seulement il serait préférable d'avoir un `setter` classique (réserve les attributs aux seuls lectures).

En plus, est-ce que la description devrait-elle pas être directement "codée en dur" dans la (sous-)classe qui implémente la supervision ?

```
nature = NatureList()  # creation of a nature
nature.add("Orgone", "mysterious organic energy")  # Optional addition of a new energy nature
world.set_natures(nature)  # registration
```

Pourquoi n'appliques-tu pas le même traitement que pour les `productions` par exemple: ton `World` contient le dictionnaire et tu lui ajoutes les différentes natures. J'aurais plutôt créé une classe `Nature` qui aurait un `name`, une description et éventuellement d'autre petits trucs. Côté config, cela donnerait:
```
world.add_nature(Nature("GAZ", "Un fluide qui s'enflamme"))
```





