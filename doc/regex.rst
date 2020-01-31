.. _regular_expressions:

Regular expressions in FastaChar
================================

What is a regular expression anyway?
------------------------------------

Adapted from wikipedia ::
  
  The phrase regular expressions, also called regexes, is often used to
  mean the specific, standard textual syntax for representing patterns
  for matching text. Each character in a regular expression (that is, each
  character in the string describing its pattern) is either a
  metacharacter, having a special meaning, or a regular character that
  has a literal meaning. For example, in the regex a., a is a literal
  character which matches just 'a', while '.' is a metacharacter that
  matches every character except a newline. Therefore, this regex
  matches, for example, 'a ', or 'ax', or 'a0'. Together, metacharacters
  and literal characters can be used to identify text of a given
  pattern, or process a number of instances of it. Pattern matches may
  vary from a precise equality to a very general similarity, as
  controlled by the metacharacters. For example, . is a very general
  pattern, [a-z] (match all lower case letters from 'a' to 'z') is less
  general and a is a precise pattern (matches just 'a'). The
  metacharacter syntax is designed specifically to represent prescribed
  targets in a concise and flexible way to direct the automation of text
  processing of a variety of input data, in a form easy to type using a
  standard ASCII keyboard.

In **FastaChar** we use regular expressions to parse the header
strings belonging to the sequences in fasta files. 
  
Extensive information on regular expression can be found in sources on
the internet, for example
https://www.rexegg.com/regex-quickstart.html.

How do we use regular expressions in FastaChar?
-----------------------------------------------

When **FastaChar** reads a fasta file with aligned sequences, this
file can have a number of sequences pertaining to one taxon. For the
analysis we would like to compare the sequences of this taxon with
those of other taxa. In order to select all the sequences of a given
taxon and label them with one name, the species name, **FastaChar**
needs some way of knowing how to interpret the headers in the fasta
files. This may be best illustrated using an example.


Example
.......
Let us say we have a fasta file with the following entry:

::
   >WBET001_Nototeredo_norvagica_Ms_TK
   TACTTTGTATTTTATTTTTTCTATTTGAGCGGGTTTGGT.....

Here we see that the first line is the header, as it starts with a
">". The header string is aparently composed of the lab id followed by
the species description, using an underscore to separate them. The
header format now becomes::

  {ID}_{SPECIES}

In order to specify the regular expression for the ID string, we need
to know how the other id's in this file look like. If we know that all
lab codes start with 'WBET', we could specify something like::

  WBET[0-9]+

which should be interpreted as the id starts with WBET and is followed
by at least one numerical, but nothing else. THe WBET part is taken
literal. The part between [ ] represents the position of one single
character. In this case this character can be any in the range from 0 to 9. The +
means that the preceding character (or possible characters) can be repeated.

This would work for this example, but when a different file is opened,
then this expression might not match. As an alternative approach we
could be more general. So we may say that the id may contain
alphanumeric characters and a period, and at least one character. This
translates to::

  [A-Za-z0-9\.]+

Now the first character can be anything from upper case and lower case
letters that appear in the (English) alphabet, any digits from 0 - 9
and a period. The symbol . has a special meaning in regular
expressions, so that if the literal symbol is meant, it must be
escaped by a backslash. What follows of the id string should be a
character that follows the same restriction as the first character
does, as indicated by the + symbol.

This representation would match our example WBTE001, but also 
PC025239.1, or ZSM20100595. Similar considerations apply to how the
regular expression should be described for the species string.

Can we disable the use of regular expressions?
----------------------------------------------

The use of regular expression
