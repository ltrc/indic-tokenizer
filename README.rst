================
indic-tokenizer
================

Tokenizer for Indian Scripts and Roman Script

Installation
============

Download
~~~~~~~~

Download **indic-tokenizer**  from `github`_.

.. _`github`: https://github.com/irshadbhat/indic-tokenizer

Install
~~~~~~~

::

    pip install git+git://github.com/irshadbhat/indic-tokenizer.git

Example
~~~~~~~

1. **work directly with files:**

.. parsed-literal::

    ind-tokz --i inputfile --o outputfile --l hin

    --i input     <input-file>
    --o output    <output-file>
    --s           set this flag to apply sentence segmentation 
    --l language  select language (3 letter ISO-639 code)
		    Hindi       : hin
		    Urdu        : urd
		    Telugu      : tel
		    Tamil       : tam
		    Malayalam   : mal
		    Kannada     : kan
		    Bengali     : ben
		    Oriya       : ori
		    Punjabi     : pan
		    Marathi     : mar
		    Nepali      : nep
		    Gujarati    : guj
		    Bodo        : bod
		    Konkani     : kok
		    Assamese    : asm
		    Kashmiri    : kas

    rom-tokz --i inputfile --o outputfile     

    --i input   <input-file>
    --o output  <output-file>
    --s         set this flag to apply sentence segmentation

2. **using python**

.. code:: python

    >>> from irtokz import tokenize_rom
    >>> tok = tokenize_rom(split_sen=True)
    >>> text = """The first act of the film introduces the protagonists, a woman named Su-jin and a man named Chul-soo. The movie highlights their accidental meeting, followed by their subsequent courting despite their difference in social status that should have kept them apart. Kim Su-jin is a 27-year-old fashion designer, spurned by her lover, a colleague who was also a married man. Depressed, she goes to a convenience store, where she bumps into a tall, handsome man with whom she has a slight misunderstanding. Following that, she returns home and, receiving her father's forgiveness, decides to start life afresh.
    ... 
    ... One day while accompanying her father, who is the CEO of a construction firm, she coincidentally meets the man whom she earlier bumped into at the convenience store. He is Choi Chul-soo, the construction site's foreman who is studying to become an architect. Though he initially appears like a rough and dirty construction worker, Chul-soo exudes sheer masculinity in its most basic physical form. Su-jin instantly takes a liking to Chul-soo and actively courts him. There are many sweet events that take place in the occurrence of their courtship, eventually leading to their marriage.
    ... 
    ... The second act follows the couple happily settling into married life, with Chul-soo designing their dream house and Su-jin learning to become a housewife. As time passes, however, Su-jin begins to display forgetfulness, including an incident in which a fire breaks out because of a stove she'd forgotten to turn off. While Chul-soo caught the fire in time, the seriousness of the incident and others like it leads them to seek medical help.
    ... 
    ... The third act deals with Su-jin's early-onset Alzheimer's disease diagnosis, and the couple's consequent response to it. Su-jin at first experiences denial, then becomes heavily burdened by the knowledge that she will forget her husband. Nevertheless, they make the commitment to stay together and as the disease progresses, the trials the couple go through increase because of Su-jin's deteriorating memory. Finally, Su-jin makes the decision to leave their home and check herself into an assisted facility.
    ... 
    ... Despite his grief, Chul-soo remains at Su-jin's side even when she doesn't remember him, hiding his eyes behind sunglasses when he visits her so she can't see his tears. At the end of the film, Chul-soo reenacts the first time they met in the convenience store, with all of Su-jin's friends and family there. In the final scene, Su-jin is riding in a car beside her husband at sunset, and he tells her, "I love you." """
    >>> print tok.tokenize(text)
    The first act of the film introduces the protagonists , a woman named Su-jin and a man named Chul-soo .
    The movie highlights their accidental meeting , followed by their subsequent courting despite their difference in social status that should have kept them apart .
    Kim Su-jin is a 27-year-old fashion designer , spurned by her lover , a colleague who was also a married man .
    Depressed , she goes to a convenience store , where she bumps into a tall , handsome man with whom she has a slight misunderstanding .
    Following that , she returns home and , receiving her father 's forgiveness , decides to start life afresh .
    One day while accompanying her father , who is the CEO of a construction firm , she coincidentally meets the man whom she earlier bumped into at the convenience store .
    He is Choi Chul-soo , the construction site 's foreman who is studying to become an architect .
    Though he initially appears like a rough and dirty construction worker , Chul-soo exudes sheer masculinity in its most basic physical form .
    Su-jin instantly takes a liking to Chul-soo and actively courts him .
    There are many sweet events that take place in the occurrence of their courtship , eventually leading to their marriage .
    The second act follows the couple happily settling into married life , with Chul-soo designing their dream house and Su-jin learning to become a housewife .
    As time passes , however , Su-jin begins to display forgetfulness , including an incident in which a fire breaks out because of a stove she 'd forgotten to turn off .
    While Chul-soo caught the fire in time , the seriousness of the incident and others like it leads them to seek medical help .
    The third act deals with Su-jin 's early-onset Alzheimer 's disease diagnosis , and the couple 's consequent response to it .
    Su-jin at first experiences denial , then becomes heavily burdened by the knowledge that she will forget her husband .
    Nevertheless , they make the commitment to stay together and as the disease progresses , the trials the couple go through increase because of Su-jin 's deteriorating memory .
    Finally , Su-jin makes the decision to leave their home and check herself into an assisted facility .
    Despite his grief , Chul-soo remains at Su-jin 's side even when she doesn 't remember him , hiding his eyes behind sunglasses when he visits her so she can 't see his tears .
    At the end of the film , Chul-soo reenacts the first time they met in the convenience store , with all of Su-jin 's friends and family there .
    In the final scene , Su-jin is riding in a car beside her husband at sunset , and he tells her , " I love you . "
    >>> 

Contact
=======

::

    Irshad Ahmad Bhat
    MS-CSE IIITH, Hyderabad
    irshad.bhat@research.iiit.ac.in
