import json
from algo import SeatingAlgorithm


# Example usage
if __name__ == "__main__":
    # Create algorithm with custom parameters
    algorithm = SeatingAlgorithm(rows=8, cols=12, num_batches=4)

    # Generate seating
    seating = algorithm.generate_seating()

    # Validate constraints
    is_valid, errors = algorithm.validate_constraints()
    print(f"Valid: {is_valid}")
    if not is_valid:
        print("Errors:", errors)

    # Get web-friendly format
    web_data = algorithm.to_web_format()

    # Print sample of web data
    print("Sample web data:")
    print(json.dumps(web_data["seating"][0][:3], indent=2))