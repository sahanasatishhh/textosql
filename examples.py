
from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
import shutil
import os
import chromadb

client = chromadb.Client()

examples=[{
    "input": "give me total volume for the C&I segment",
    "query": "SELECT SUM(volume) AS total_volume FROM sales_data WHERE segment ILIKE 'C&I';"
},
{
  "input": "What are the last five orders billed for the C&I segment in the east region?",
  "query": "SELECT segment, region, area_manager, delivery_plant, product_category, volume, billing_date FROM sales_data WHERE segment ILIKE 'C&I' AND region ILIKE 'East' ORDER BY billing_date DESC LIMIT 5;"
},
{
    "input": "give me Total Volume Sales for Category-1, Category-2",
    "query": "SELECT COALESCE(product_category, 'Total') AS product_category, SUM(volume) AS total_volume FROM sales_data WHERE product_category ILIKE 'Category-1' OR product_category ILIKE 'Category-2' GROUP BY GROUPING SETS ((product_category), ());"
},
{
    "input": "Zone Wise Volume totals for a Category-20",
    "query": "SELECT COALESCE(region,'All Regions') AS region, COALESCE(segment, 'Total') AS segment, SUM(volume), product_category AS total_volume FROM sales_data WHERE product_category ILIKE 'Category-20%' GROUP BY GROUPING SETS ((segment, region, product_category), (region), ()) ORDER BY  region, segment;"
},

{
  "input": "Give me volume totals for each business unit zoneWise",
  "query": "SELECT COALESCE(region,'All Regions') AS region, COALESCE(segment, 'Total') AS segment, SUM(volume) AS total_volume FROM sales_data GROUP BY GROUPING SETS ((segment, region), (region), ()) ORDER BY  region, segment;"
},

{
    "input": "Give me volume total for each business unit for AM-Telangana",
    "query": "SELECT COALESCE(segment, 'Total') AS segment, SUM(volume) AS total_volume FROM sales_data WHERE area_manager ILIKE 'AM - Telangana%' GROUP BY GROUPING SETS ((segment), ()) ORDER BY segment;"
},
{
    "input": "Total Volume Sales Zone-Wise for all Units",
    "query": "SELECT COALESCE(region, 'All Regions') AS region, SUM(volume) AS total_volume FROM sales_data GROUP BY GROUPING SETS ((region), ()) ORDER BY region;"
}]



from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_huggingface import HuggingFaceEmbeddings




def get_example_selector():
    collection = client.get_or_create_collection("example_selector")

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
 

    example_selector =SemanticSimilarityExampleSelector.from_examples(
        examples,
        embedding_model,
        Chroma,
        k=2,
        input_keys=["input"],
    )
    return example_selector
