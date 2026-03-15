from thumbnail import ThumbnailGenerator

generator = ThumbnailGenerator(output_dir=".")

# Test 1: Pork Alert
generator.generate_thumbnail({
    "bill_id": "HR 101",
    "fluff_detected": True,
    "sponsor_contact_info": {"sponsor_name": "Senator Ted Cruz"}
})

# Test 2: Clean Bill
generator.generate_thumbnail({
    "bill_id": "S 202",
    "fluff_detected": False,
    "sponsor_contact_info": {"sponsor_name": "Senator Elizabeth Warren"}
})
