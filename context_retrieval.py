from pymilvus import MilvusClient, DataType

client = MilvusClient("research_paper.db")
schema = client.create_schema(
    auto_id=True,
    enable_dynamic_fields= True,
)
schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=1024)
schema.add_field("text", DataType.VARCHAR, max_length=65535)

index_params = client.prepare_index_params()
index_params.add_index("embedding", index_type="IVF_FLAT", metric_type="COSINE")

client.create_collection(
    collection_name="context_engineering",
    data = [{"text":chunk,"embedding":emb}]
)