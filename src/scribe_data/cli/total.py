issue #159 - Remove the code that generates them from the new function

https://github.com/scribe-org/Scribe-Data/issues/144 adding time stamp

move convert json to csv and tsv into convert.py file - https://github.com/scribe-org/Scribe-Data/issues/145 -> check issue comments as well

Lastly - https://github.com/scribe-org/Scribe-Data/issues/147 -> issue comment

query.py te qID pass korleo result dibe

"""

Functions to check the total language data available on Wikidata.



.. raw:: html

 <!--

 * Copyright (C) 2024 Scribe

 *

 * This program is free software: you can redistribute it and/or modify

 * it under the terms of the GNU General Public License as published by

 * the Free Software Foundation, either version 3 of the License, or

 * (at your option) any later version.

 *

 * This program is distributed in the hope that it will be useful,

 * but WITHOUT ANY WARRANTY; without even the implied warranty of

 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the

 * GNU General Public License for more details.

 *

 * You should have received a copy of the GNU General Public License

 * along with this program. If not, see <https://www.gnu.org/licenses/>.

 -->

"""

#!/usr/bin/env python3

from SPARQLWrapper import SPARQLWrapper, JSON



def get_total_lexemes(language=None, data_type=None, all=False):

 endpoint_url = "https://query.wikidata.org/sparql"

 sparql = SPARQLWrapper(endpoint_url)



 query= """

 SELECT (COUNT(DISTINCT ?lexeme) as ?total)

 WHERE {

 ?lexeme a ontolex:LexicalEntry .

 """



if language:

 query += f"?lexeme dct:language wd:{language} .\n"

if data_type:

 query += f"?lexeme wikibase:lexicalCategory wd:{data_type} .\n"



 query += "}"



 sparql.setQuery(query)

 sparql.setReturnFormat(JSON)

 results = sparql.query().convert()



return int(results["results"]["bindings"][0]["total"]["value"])