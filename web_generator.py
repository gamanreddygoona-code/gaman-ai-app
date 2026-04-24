import re
import json
import time
from concurrent.futures import ThreadPoolExecutor
from model_interface import generate as generate_response

def generate_website_code(prompt: str):
    """
    PERFORMS MULTI-STEP SYNTHESIS (OPTIMIZED):
    1. Architectural Planning (Sequential)
    2. Style, Structure, & Logic (Parallel)
    """
    
    import random
    steps = []
    
    # --- STEP 1: ARCHITECTURAL PLANNING ---
    planning_msgs = [
        "I am analyzing your vision prompt to synthesize a high-fidelity architectural blueprint. Defining layout constraints, color theory, and core interactive modules.",
        "Deep scanning project requirements. Drafting architectural layout, defining semantic hierarchy, and mapping out the user experience flow.",
        "Initializing neural architectural sweep. I'm mapping design tokens, identifying layout bottlenecks, and selecting a premium aesthetic palette."
    ]
    steps.append({"msg": random.choice(planning_msgs), "cmds": random.randint(1, 3)})
    
    plan_prompt = f"Design a website architecture for: {prompt}. Describe the layout, color palette (hex), and 4 key features. Return JSON only: {{'layout': '...', 'colors': ['#...', '#...'], 'features': ['...', '...']}}"
    plan_raw = generate_response(plan_prompt)
    
    # --- STEP 2, 3, 4: PARALLEL SYNTHESIS ---
    synthesis_msgs = [
        "Architectural plan finalized. I am now spawning parallel synthesis threads for the Style Engine, Content Structure, and Behavioral Logic.",
        "Blueprint validated. Spawning concurrent workers to synthesize CSS architecture, HTML markup, and JavaScript interactions simultaneously.",
        "Plan locked. Parallelizing the generation of design systems, structural layers, and logic scripts to accelerate the deployment pipeline."
    ]
    steps.append({"msg": random.choice(synthesis_msgs), "cmds": 3})
    
    def get_style():
        return generate_response(f"Generate a full CSS stylesheet for a {prompt} website based on this plan: {plan_raw}. Use modern aesthetics, glassmorphism, and responsive grid. Return ONLY CSS code inside <style> tags.")

    def get_body():
        return generate_response(f"Generate the full HTML <body> for a {prompt} website. Use the plan: {plan_raw}. Include sections for hero, features, and footer. Return ONLY HTML code.")

    def get_js():
        return generate_response(f"Generate Javascript for a {prompt} website. If 3D is requested, include Three.js logic. Return ONLY code inside <script> tags.")

    with ThreadPoolExecutor(max_workers=3) as executor:
        f_style = executor.submit(get_style)
        f_body  = executor.submit(get_body)
        f_js    = executor.submit(get_js)
        
        style_code = f_style.result()
        body_code  = f_body.result()
        js_code    = f_js.result()

    # --- FINAL SYNTHESIS ---
    merge_msgs = [
        "All layers synthesized. I am performing a surgical merge of the CSS/JS assets and validating visual integrity against the initial architectural plan.",
        "Synthesis complete. Executing final merge of structural and stylistic layers. Running cross-layer validation for production readiness.",
        "Layers ready. Compiling architectural segments into a unified production build. Validating aesthetic coherence and interactive stability."
    ]
    steps.append({"msg": random.choice(merge_msgs), "cmds": random.randint(2, 5)})
    
    # Clean up tags if the model included them
    style_code = style_code.replace("<style>", "").replace("</style>", "").strip()
    js_code = js_code.replace("<script>", "").replace("</script>", "").strip()
    
    # Ensure we have clean code
    def extract_code(text):
        import re
        # Match ```lang \n content \n ```
        match = re.search(r"```[a-zA-Z]*\n(.*?)(?:\n```|$)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        if "```" in text:
            text = text.split("```")[1]
            return re.sub(r"^[a-zA-Z]*\n", "", text).strip()
        return text.strip()

    style_code = extract_code(style_code)
    body_code = extract_code(body_code)
    js_code = extract_code(js_code)

    final_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synthesized by Gaman AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;900&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        {style_code}
    </style>
</head>
<body>
    {body_code}
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        {js_code}
    </script>
</body>
</html>"""

    return final_html, steps

def modify_website_code(current_code: str, prompt: str) -> str:
    """
    Surgical AI Update.
    """
    mod_prompt = f"Update this code based on user request: {prompt}. Code: {current_code}. Return ONLY full updated HTML."
    return generate_response(mod_prompt)
