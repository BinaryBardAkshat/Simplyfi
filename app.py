import streamlit as st
import ast
import graphviz
from graphviz import Digraph
import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import google.generativeai as genai

# Page configuration
st.set_page_config(page_title="Simplyfi", layout="wide")

# Access the API key from secrets.toml
api_key = st.secrets["general"]["API_KEY"]

# Configure Gemini API
genai.configure(api_key=api_key)

# Function to generate syntax-highlighted code
def syntax_highlight(code, language):
    try:
        lexer = get_lexer_by_name(language)
        formatter = HtmlFormatter(style="colorful", full=True, noclasses=True)
        return highlight(code, lexer, formatter)
    except Exception as e:
        st.error(f"Syntax highlighting failed: {e}")
        return code

# Function to generate AST (Python only)
def generate_ast(code):
    try:
        tree = ast.parse(code)
        dot = Digraph()
        
        def add_nodes(node, parent=None):
            if isinstance(node, ast.AST):
                node_name = f"{node.__class__.__name__}_{id(node)}"
                dot.node(node_name, label=node.__class__.__name__)
                if parent:
                    dot.edge(parent, node_name)
                for child in ast.iter_child_nodes(node):
                    add_nodes(child, node_name)
            else:
                leaf_name = f"{str(node)}_{id(node)}"
                dot.node(leaf_name, label=str(node))
                if parent:
                    dot.edge(parent, leaf_name)

        add_nodes(tree)
        return dot
    except SyntaxError:
        st.error("The provided code does not appear to be valid Python syntax.")
        return None

# Generalized function to generate a flowchart for any language
def generate_flowchart(code):
    flowchart = Digraph()
    lines = code.splitlines()
    
    # Add start node
    flowchart.node("start", "Start", shape="ellipse", style="filled", color="lightblue")
    previous = "start"
    
    # Regex patterns to detect main function structures in various languages
    func_patterns = [
        re.compile(r"def\s+(\w+)\s*\("),       # Python
        re.compile(r"function\s+(\w+)\s*\("),  # JavaScript
        re.compile(r"(\w+\s+)?(\w+)\s*\("),    # Java, C, C++, C#
    ]
    
    for line in lines:
        if line.strip().startswith("//") or line.strip().startswith("#"):  # Comment step
            node = line.strip().lstrip("//#").strip()
            flowchart.node(node, node, shape="box", style="rounded,filled", color="lightgrey")
            flowchart.edge(previous, node)
            previous = node
        else:
            for pattern in func_patterns:
                match = pattern.match(line.strip())
                if match:  # New function detected as a major step
                    func_name = match.group(2) if len(match.groups()) > 1 else match.group(1)
                    flowchart.node(func_name, func_name, shape="parallelogram", style="filled", color="lightyellow")
                    flowchart.edge(previous, func_name)
                    previous = func_name

    # Add end node
    flowchart.node("end", "End", shape="ellipse", style="filled", color="lightblue")
    flowchart.edge(previous, "end")
    return flowchart

# Sidebar setup with navigation
st.sidebar.write("### Welcome to Simplyfi!")
st.sidebar.write("Simplyfi - Multi-Language Code Visualization Tool")
nav_option = st.sidebar.radio("Navigate", ["Home", "ChatWithCode", "Contribute", "Instructions", "Tutorials"])

# Instructions and Cautions
st.sidebar.header("Instructions and Cautions")
st.sidebar.write("### Instructions:")
st.sidebar.write("""
- **Navigate through the app** using the options in the sidebar.
- **Use the 'Generate Visuals' section** to enter your code, select the language, and visualize the syntax tree and flowchart.
- **In 'ChatWithCode',** paste your code to get an explanation from the AI.
- **Visit 'Contribute'** to find links to my GitHub and contributions.
""")
st.sidebar.write("### Cautions:")
st.sidebar.write("""
- **Ensure a stable internet connection** for optimal performance.
- **Avoid sharing sensitive personal information** in the chat section.
- If you encounter issues, try **refreshing the page or restarting the app.**
""")

if nav_option == "Home":
    st.title("Simplyfi - Multi-Language Code Visualization Tool")
    st.write("### Instructions")
    st.write("1. Enter your code and select the language.\n2. Click 'Generate Visuals' to view the syntax tree, flowchart, and dependency graph.\n3. Use ChatWithCode for code explanations.\n4. Visit Contribute for links to my work.")

    # Visual generation section
    st.header("Generate Visuals")
    code_input = st.text_area("Enter your code here:", height=300)
    language = st.selectbox("Select Language:", ["Python", "JavaScript", "Java", "C++", "C#"])
    if st.button("Generate Visuals"):
        if code_input.strip():
            # Flowchart for any language
            st.header("Flowchart")
            flowchart = generate_flowchart(code_input)
            st.graphviz_chart(flowchart)

elif nav_option == "ChatWithCode":
    st.title("ChatWithCode")
    chat_code = st.text_area("Paste code here", height=300)
    user_prompt = st.text_input("Additional Prompt (optional)")

    if st.button("Explain Code"):
        if chat_code.strip():
            # Pre-configured prompt with user input
            prompt = f"Explain this code in short: {chat_code}. {user_prompt}" if user_prompt else f"Explain this code in short: {chat_code}"
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                st.write("### Explanation")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error with Gemini API: {e}")

elif nav_option == "Contribute":
    st.title("Contribute")
    st.write("Thank you for considering contributing to **Simplyfi**!")
    
    st.write("### Instructions:")
    st.write("""
    1. **Clone or Fork the Repository**:
        - Clone the repository using:
          ```bash
          git clone https://github.com/binarybardakshat/simplyfi.git
          ```
        - Or fork the repository to your GitHub account.
    2. **Add Your Features or Fix Bugs**:
        - Feel free to add new features or fix any existing bugs. Your creativity is welcome!
    3. **Push Your Changes**:
        - After making your changes, commit them and push the repository back to GitHub:
          ```bash
          git add .
          git commit -m "Your descriptive message here"
          git push origin main
          ```
    4. **Create Issues**:
        - If you have ideas for new features or encounter bugs that need attention, please create an issue in the repository. This helps keep track of tasks and enhancements.
    """)

    st.write("### Contribution Guidelines:")
    st.write("""
    - **Creativity and Transformation**: There are no limits to your creativity or transformation ideas. Feel free to think outside the box and explore innovative solutions!
    - **Collaboration**: We believe in the power of collaboration. Discuss your ideas in the issue tracker, and work together with others to enhance Simplyfi.
    """)

    st.write("### How It Works:")
    st.image("resources/work.png")  # Replace with the actual path to your diagram

    st.write("### Get Your Gemini API Key:")
    st.write("You can obtain your Gemini API key [here](https://link-to-gemini-api.com).")  # Replace with the actual link
    st.write("### Save the API Key:")
    st.write("After obtaining your API key, save it in the `/streamlit/secrets.toml` file as follows:")
    st.code("""
    [API_KEY]
    API_KEY = "your_api_key_here"
    """)
    st.write("### Create New Features:")
    st.write("You’re encouraged to create any new features you desire. Let your imagination lead the way!")

    st.write("For any queries or assistance, feel free to reach out to me at: [binarybardakshat@gmail.com](mailto:binarybardakshat@gmail.com)")

elif nav_option == "Instructions":
    st.title("Instructions")
    st.write("### Simplyfi - Multi-Language Code Visualization Tool")
    st.write("1. **Home**: Enter your code and select the programming language to visualize its syntax tree and flowchart.")
    st.write("2. **ChatWithCode**: Paste your code to get an AI explanation of its functionality.")
    st.write("3. **Contribute**: Learn how to contribute to this project.")
    st.write("4. **Tutorials**: Access upcoming tutorials on effective usage.")
    st.write("### Tips for Effective Use:")
    st.write("1. Ensure your code is properly formatted to avoid syntax errors in visualizations.")
    st.write("2. For any assistance, you can always check the documentation or contact me.")

elif nav_option == "Tutorials":
    st.title("Tutorials")
    st.write("Coming Soon! Stay tuned for tutorials on how to use Simplyfi effectively.")
