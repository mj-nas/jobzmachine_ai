import json
from sentence_transformers import InputExample
from sentence_transformers import SentenceTransformer, LoggingHandler, losses, evaluation
from torch.utils.data import DataLoader



# setup the model and tokenizer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")
model = SentenceTransformer("BAAI/bge-large-en") 

# setup training examples

with open("resumes.json") as f:
    data = json.load(f)

resume_data = data["data"]["resumes"]

# Example JD
job_description = "Looking for an Epic medical billing specialist with 3+ years experience"

# Create training examples: relevant and not relevant
train_examples = []

for i, resume in enumerate(resume_data):
    content = " ".join(resume["content"])  # Flatten content list into a string

    # Example logic:
    if "Epic" in content and "billing" in content and "3 years" in content:
        label = 1.0
    else:
        label = 0.0

    example = InputExample(texts=[job_description, content], label=label)
    train_examples.append(example)


# setup training parameters
num_epochs = 1
batch_size = 16
warmup_steps = int(0.1 * len(train_examples))  # Warmup steps for learning rate scheduler


with open("resumes.json") as f:
    data = json.load(f)

resume_data = data["data"]["resumes"]

# Example JD
job_description = "Looking for an Epic medical billing specialist with 3+ years experience"

# Create training examples: relevant and not relevant
train_examples = []

for i, resume in enumerate(resume_data):
    content = " ".join(resume["content"])  # Flatten content list into a string

    # Example logic:
    if "Epic" in content and "billing" in content and "3 years" in content:
        label = 1.0
    else:
        label = 0.0

    example = InputExample(texts=[job_description, content], label=label)
    train_examples.append(example)


    # fine tune the model
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)
train_loss = losses.CosineSimilarityLoss(model)


# Create the model and train it
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=num_epochs,
    warmup_steps=warmup_steps,
    show_progress_bar=True,
    use_amp=True,
    # output_path="fine_tuned_model",
)
# Save the model
model.save("modles/bge-local-fine_tunedv1")
