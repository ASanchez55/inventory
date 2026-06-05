document.addEventListener("DOMContentLoaded", function () {
    function setupLookupModal(config) {
        const form = document.getElementById(config.formId);
        const select = document.getElementById(config.selectId);
        const alertBox = document.getElementById(config.alertId);
        const fieldError = document.getElementById(config.fieldErrorId);
        const nameInput = document.getElementById(config.nameInputId);
        const modalElement = document.getElementById(config.modalId);

        if (!form || !select || !alertBox || !fieldError || !nameInput || !modalElement) {
            return;
        }

        const modalInstance = bootstrap.Modal.getOrCreateInstance(modalElement);

        function clearErrors() {
            alertBox.textContent = "";
            alertBox.classList.add("d-none");
            fieldError.textContent = "";
            fieldError.classList.add("d-none");
            nameInput.classList.remove("is-invalid");
        }

        function upsertOption(item) {
            const existingOption = select.querySelector(`option[value="${item.id}"]`);
            if (existingOption) {
                existingOption.textContent = item.name;
                existingOption.selected = true;
                return;
            }

            const option = new Option(item.name, item.id, true, true);
            select.add(option);

            const options = Array.from(select.options);
            const placeholder = options.find((candidate) => candidate.value === "");
            const sortedOptions = options
                .filter((candidate) => candidate.value !== "")
                .sort((left, right) => left.text.localeCompare(right.text));

            select.innerHTML = "";
            if (placeholder) {
                select.add(placeholder);
            }
            sortedOptions.forEach((candidate) => select.add(candidate));
            select.value = String(item.id);
        }

        form.addEventListener("submit", async function (event) {
            event.preventDefault();
            clearErrors();

            const formData = new FormData(form);

            try {
                const response = await fetch(form.dataset.url, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                    },
                    body: formData,
                });

                const payload = await response.json();

                if (!response.ok) {
                    const nameErrors = payload.errors && payload.errors.name ? payload.errors.name : [];
                    if (nameErrors.length > 0) {
                        fieldError.textContent = nameErrors.join(" ");
                        fieldError.classList.remove("d-none");
                        nameInput.classList.add("is-invalid");
                    } else {
                        alertBox.textContent = "Unable to save. Please try again.";
                        alertBox.classList.remove("d-none");
                    }
                    return;
                }

                upsertOption(payload[config.payloadKey]);
                form.reset();
                clearErrors();
                modalInstance.hide();
            } catch (error) {
                alertBox.textContent = "Something went wrong while saving. Please try again.";
                alertBox.classList.remove("d-none");
            }
        });

        modalElement.addEventListener("hidden.bs.modal", function () {
            form.reset();
            clearErrors();
        });
    }

    setupLookupModal({
        modalId: "categoryModal",
        formId: "categoryModalForm",
        selectId: "id_category",
        alertId: "categoryModalAlert",
        fieldErrorId: "categoryModalNameError",
        nameInputId: "categoryModalName",
        payloadKey: "category",
    });

    setupLookupModal({
        modalId: "brandModal",
        formId: "brandModalForm",
        selectId: "id_brand",
        alertId: "brandModalAlert",
        fieldErrorId: "brandModalNameError",
        nameInputId: "brandModalName",
        payloadKey: "brand",
    });
});
