# MCP

Here is a short installation and setup guide for [Jan](https://github.com/janhq/jan) on Linux
to communicate with a remote [Ollama](https://github.com/ollama/ollama) server
and bind an MCP server.

The instructions can be loosely applied to a Windows environment as well.

## Prerequisites

* **Jan Desktop App:**
  Linux AppImage download at [jan.ai](https://jan.ai).
* **Remote-Ollama:**
  The server `http://YOUR-OLLAMA-SERVER.local:11434/v1` must be running
  and accessible.
* **Local MCP Server:**
  The Python script is available locally
  (e.g. under `~/projects/mcp-ask-relearn/mcp_askrelearn.py`).

---

### 1. Installation of Jan and connection to the remote Ollama

1. **Downloading and starting Jan:**

   Install *Jan* via the package management of your distribution,
   if applicable.
   (For *Manjaro* (& *Arch*) available as AUR package: `pamac install jan-bin`,
   if AUR support is enabled.)

   Alternatively, installation as AppImage is possible:
   Download the file `Jan_x.y.z_amd64.AppImage`[^1],
   make it executable and start the program:

    ```bash
    chmod +x Jan-x.x.x-x_linux_amd64.AppImage
    ## start program:
    ./Jan-x.x.x-x_linux_amd64.AppImage
    ```

    [^1]: https://github.com/janhq/jan/releases

   0. Open the Jan application and go to the **Settings** -> **Privacy** area.
      Decide using the slider switch whether **Analytics** should remain enabled.

2. **Adjust API configuration:**

   1. Open the Jan application and go to the **Settings** area. Next to the
      section header **Model Providers** (bottom in the middle column),
      click the **[+]** sign (-> "*Add OpenAI Provider*").

   2. In the **Add OpenAI Provider** dialog, select a name for the provider:
      e.g. "*Supercomputer Ollama*". Click on **[Create]**.

      On the right, you can now see configuration options for the provider just
      created above the name specified.

   3. Enter the following address under **Base URL**: `http://YOUR-OLLAMA-SERVER.local:11434/v1`

      The API key is not used; enter `ollama`.

   4. Under **Models** -- if necessary after clicking on **⭮ Refresh** -- a list
      of selectable models on the Ollama instance should appear.

   5. It seems necessary to manually mark a model as tool-supporting -- the support does not
      seem recognizable from the model metadata at Ollama or via the OpenAI API (for *Jan*).

      1. To do this, click on the **🖉 pencil** symbol in this list to edit for suitable models
         (e.g. "*glm-4.7-flash:q8_0*").
      2. Under **Capabilities**, slide the **Tools** switch to *active*.

   3. Create or select a chat.

      Select the appropriate model installed on the **remote** computer (*supercomputer*) thre
      (e.g. "*glm-4.7-flash:q8_0*") and -- regarding section 2 -- knows how to handle MCP tools.

      Tool support is displayed by a wrench icon.

---

### 2. Integrating the local MCP server

So that Jan can use locally running Python applications as an MCP server,
configure these in the Jan interface:

0. **MCP project/script installation:**
   Clone/store the Python MCP project on the Linux machine at a known location
   (e.g. `~/projects/`).

1. Make sure a virtual environment is initialized; if the project uses a `pyproject.toml`
   file and `uv`, switch to the project directory (e.g. `~/projects/mcp-ask-relearn/`) and
   run `uv sync --frozen`.

2. **Locate the MCP server script:**
   Locate the MCP server Python script (e.g. `~/projects/mcp-ask-relearn/mcp_askrelearn.py`).

3. **Open MCP settings:**
   Go in the Jan menu to **Settings** -> **MCP Servers**.

4. **Add server:**
   Click the **[+ Add MCP Server]** button in the **MCP Servers** section on the right.

   Jan presents input fields under the heading **Add MCP Server**.

   Enter the following details for the local Python script server:

    * **Server Name:** `Ask Relearn`
    * **Transport Type:** `STDIO`
    * **Command:** `uv`
    * **Arguments:**
      1. `--directory`
      2. The full path to the script, e.g. `/home/user/projects/mcp-ask-relearn`
      3. `run`
      4. `--frozen`
      5. The name of the script, e.g. `mcp_askrelearn.py`
      6. `--base-url`
      7. The name base url of your Relearn site, e.g. `http://localhost:1313`
      8. `--description`
      9. An appropriate description of your site and tool,
         e.g. `Search for help about the given search term in the documentation provided
         by the static site builder Hugo and the Relearn theme.`

   In case errors occur -- especially if referring to missing modules --,
   set the following environment variables (empty):

    * **Environment Variables**
      1. `PYTHONHOME` :: *empty*

   Click **Save** to save.

5. **Test connection:**
   After saving, the server should appear under "Running MCP Servers".
   Enable it when ready by sliding the switch on the right edge of the server section
   to the right.

6. **Usage:**
    The tools provided by the script can now be used in the Jan chat interface.
    Before intended use by a model, the user will be asked for consent once per session.
