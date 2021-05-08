# Road Deaths

This project aims to catalogue every one of the over 494,638 [traffic crash](https://crashnotaccident.com/) deaths the [United Kingdom of Great Britain and Northern Ireland](https://en.wikipedia.org/wiki/United_Kingdom) since [1896](https://en.wikipedia.org/wiki/Death_of_Bridget_Driscoll).

### Adding and updating entries

Add data is stored in two places: `incidents.yml` and `_data/annual_stats.yml`.
`incidents.yml` contains all the incident data, while `_data/annual_stats.yml` contains the totals for each year where available.

After editing you'll need to open the shell or terminal and run the following command which will update the website held in `index.html`:

```shell
python3 _data/generate-pages.py
```

### Limitations

- The project isn't really set up to accurately describe the crash timeline. For example, it struggles to describe when the person to _blame_ died.
- Linked pages often get deleted. Police witness appeals especially get removed after a time meaning valuable source data is lost. Each incident should probably have its own incident file so allow for the story of each death to be told.
- 494,638 deaths and approximately 5 more per day make for one person to record. I'll be honest, cataloguing children being killed either on the pavement or even in their buggy is especially hard.
- ...
