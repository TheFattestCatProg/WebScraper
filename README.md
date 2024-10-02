# Info
This project provides single-threaded asynchronous scrapper which you can configure using yaml-files.
Each yaml-file describes rules how to parse current web-resource.

## Requirements
To install dependencies run:
```bash
pip install -r requirements.txt
```

## Run
To run this program:
```bash
python webscrapper.py config.yaml
```

# Yaml Format
Yaml-config consists of rules of the following format:
```yaml 
rule-name:
    mode: some-mode
    param1: ...
    param2: ...
    ...
```
Program starts executing by reading main rule:
```yaml
main:
    url: some-url.url
    next: next-rule
```
Next rule means "I fetch this url and go to 'next-rule' with this data".
It's like `main().next-rule().scrap()`, `array.map(..).filter(..)` in programming.

In `modes.py` declared all mode this scrapper supports.
**You could add your own modes**.

## Basic modes
- `hub`:
    This rule is like **map** function in programming languages.
    It selects all \<a>-urls by selector and apply next rule to all of it.
    ```yaml
    example-hub:
        mode: hub
        sel: a.class1.class2 # BeautifulSoup selector
        next: other-rule
    ```

- `loop`:
    This rule is like **while** cycle. It applies rule to current page, follows
    next selected url and repeats.
    ```yaml
    example-loop:
        mode: loop
        sel: a.class1.class2 # BeautifulSoup selector
        next: other-rule
    ```

- `article`:
    This rule parses current page and saves in specified directory. Name of file is unique number. Format of saving: [title]\n[paragraphs separated by \n].
    Each sentence takes up a separate line. Sometimes it's buggy because of 
    stupid developers of websites.
    ```yaml
    # There may be some changes if i forgot to edit readme
    example-article:
        mode: article
        sel-title: p.title # BeautifulSoup selector
        sel-body: p.body
        ignore: [ table ]  # Some tags to ignore
        dir: some/dir/     # Directory to save files
    ```

## Your own modes
In `modes.py` file you can easily describe your own parsing modes.
API is easy so see code.

Note that `"-"` in parameter names is replaced by `"_"` at code execution.
So, `param-one` in `modes.py` must be described as `param_one`.