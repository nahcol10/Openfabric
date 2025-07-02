import os
import logging
import base64
from typing import Dict

from memory.short_term_memory import get_redis_history, chain_with_history

from session_manager import SessionManager
from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel, State
from core.stub import Stub


# Global instances
session_manager = SessionManager()
configurations: Dict[str, ConfigClass] = dict()
OUTPUT_FOLDER = "output_3d_model"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


############################################################
# Config callback function
############################################################
def config(configuration: Dict[str, ConfigClass], state: State) -> None:
    """
    Stores user-specific configuration data.

    Args:
        configuration (Dict[str, ConfigClass]): A mapping of user IDs to configuration objects.
        state (State): The current state of the application (not used in this implementation).
    """
    for uid, conf in configuration.items():
        logging.info(f"Saving new config for user with id:'{uid}'")
        configurations[uid] = conf


############################################################
# Execution callback function
############################################################
def execute(model: AppModel) -> None:
    """
    Main execution entry point for handling a model pass with session and memory management.

    Args:
        model (AppModel): The model object containing request and response structures.
    """
    # Get the username from request, or use default
    user_id = "super-user"
    username = model.request.username
    if username:
        session = session_manager.get_session(username)
    else:
        session = session_manager.get_session(user_id)
    # Try to get existing session for the user
    existing_sessions = [s for s in session_manager.sessions.values()
                       if s.user_id == username and s.is_active]
    session = existing_sessions[0] if existing_sessions else None

    if not session:
        session = session_manager.create_session(username)
        logging.info(f"Created new session: {session.session_id}")
    
    logging.info(f"User ID: {username}, Session ID: {session.session_id}")

    # Check for session timeout
    if session_manager.check_session_timeout(session.session_id):
        logging.info(f"Session {session.session_id} has timed out")
        session_manager.end_session(
            session.session_id
        )  # This will store memory summary
        model.response.message = "Session has timed out. Please create a new session."
        return

    # Update session activity
    session.update_activity()

    # Retrieve input
    request: InputClass = model.request

    # Get relevant context from memory
    try:
        context_msgs = session.memory.fetch_context(request.prompt)
    except Exception as e:
        logging.warning(f"Memory fetch failed, using empty context: {e}")
        context_msgs = []

    # 2. Pass it into the LLM
    llm_response = chain_with_history.invoke(
        {
            "input": request.prompt,
            "history": context_msgs,  # << inject manually here
        },
        config={"configurable": {"session_id": session.session_id}},
    )

    # Get Redis history for this session
    history = get_redis_history(session.session_id)

    # Store user's prompt in memory
    try:
        history.add_user_message(request.prompt)
        history.add_ai_message(llm_response.content)
    except Exception as e:
        logging.warning(f"Failed to store messages in memory: {e}")

    try:
        # Retrieve user config
        user_config = configurations.get(user_id, None)
        logging.info(
            f"Session {session.session_id} - Message count: {session.message_count}"
        )

        # Initialize the Stub with app IDs
        app_ids = user_config.app_ids if user_config else []
        stub = Stub(app_ids)

        # Step 1: Generate image from text using text-to-image API
        text_to_image_response = stub.call(
            "c25dcd829d134ea98f5ae4dd311d13bc.node3.openfabric.network",
            {"prompt": llm_response.content},
            user_id,
        )

        if text_to_image_response is None:
            raise Exception("Text-to-image API call failed")

        generated_image = text_to_image_response.get("result")
        if not generated_image:
            raise Exception("No image was generated")

        # Save intermediate image with session-specific name
        image_path = OUTPUT_FOLDER + f"/output_{session.session_id}.png"
        with open(image_path, "wb") as f:
            f.write(generated_image)

        logging.info(
            f"Session {session.session_id} - Generated image saved to {image_path}"
        )

        # Convert image to base64 for API input
        image_base64 = base64.b64encode(generated_image).decode("utf-8")

        # Step 2: Generate 3D model from the image using image-to-3D API
        image_to_3d_response = stub.call(
            "5891a64fe34041d98b0262bb1175ff07.node3.openfabric.network",
            {"input_image": image_base64},
            user_id,
        )

        if image_to_3d_response is None:
            raise Exception("Image-to-3D API call failed")

        # Get both the 3D model and preview video
        model_3d = image_to_3d_response.get("generated_object")
        if not model_3d:
            raise Exception("No 3D model was generated")
        preview_video = image_to_3d_response.get("video_object")
        if not preview_video:
            logging.warning(
                f"Session {session.session_id} - No preview video generated"
            )

        # Save 3D model if generated
        model_3d_path = OUTPUT_FOLDER + f"/output_{session.session_id}.glb"
        with open(model_3d_path, "wb") as f:
            f.write(model_3d)
        logging.info(
            f"Session {session.session_id} - Generated 3D model saved to {model_3d_path}"
        )

        # Save preview video if generated
        if preview_video:
            preview_video_path = OUTPUT_FOLDER + f"/preview_{session.session_id}.mp4"
            with open(preview_video_path, "wb") as f:
                f.write(preview_video)
            logging.info(
                f"Session {session.session_id} - Generated preview video saved to {preview_video_path}"
            )

        output_response: OutputClass = model.response
        success_message = f"Successfully generated 3D model from prompt (Session: {session.session_id})"
        output_response.message = success_message

        # Store AI response in memory
        try:
            history.add_ai_message(success_message)
        except Exception as mem_error:
            logging.warning(f"Failed to store success message in memory: {mem_error}")

    except Exception as e:
        error_message = f"Error: {str(e)}"
        logging.error(
            f"Session {session.session_id} - Error during processing: {str(e)}"
        )
        
        output_response: OutputClass = model.response
        output_response.message = error_message

        # Store error message in memory
        try:
            history.add_ai_message(error_message)
        except Exception as mem_error:
            logging.warning(f"Failed to store error message in memory: {mem_error}")

        # End session on critical errors
        if "API call failed" in str(e):
            session_manager.end_session(
                session.session_id
            )  # This will store memory summary
