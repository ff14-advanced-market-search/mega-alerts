def create_oribos_exchange_pet_link(realm_name, pet_id, region):
    fixed_realm_name = realm_name.lower().replace("'", "").replace(" ", "-")
    if region == "NA":
        url_region = "us"
    else:
        url_region = "eu"
    return f"https://oribos.exchange/#{url_region}-{fixed_realm_name}/82800-{pet_id}"
