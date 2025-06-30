import streamlit as st
import asyncio
import os
from agents import configure_team, start_task

st.title("Magentic-One Chatbot")

default_task = "What color is the sky?"
task = st.text_area("Task: ", default_task)
clicked = st.button("Run!")
# Create a container for messages
answer_container = st.container()
message_container = st.container()

if clicked:

    async def run_task_with_streaming(task):
        try:
            with st.spinner("Initializing Magentic-One..."):
                team, model_client = await configure_team()

            with message_container:
                st.write("🤖 **Magentic-One is working...**")
                st.divider()

                message_count = 0
                final_result = None

                async for msg in start_task(team, model_client, task):
                    message_count += 1

                    # Check if this is the final summary message
                    if hasattr(msg, "messages") and hasattr(msg, "stop_reason"):
                        # This is the final result message - don't display it as a regular message
                        final_result = msg
                        break

                    # Display regular messages in real-time
                    source = getattr(msg, "source", "unknown")
                    content = getattr(msg, "content", str(msg))
                    msg_type = getattr(msg, "type", "Unknown")
                    models_usage = getattr(msg, "models_usage", None)
                    metadata = getattr(msg, "metadata", {})

                    # Display based on source
                    if source == "user":
                        with st.chat_message("user"):
                            st.markdown(content)

                            # Show metadata in expander
                            with st.expander("📋 Message Details", expanded=False):
                                st.json(
                                    {
                                        "Source": source,
                                        "Type": msg_type,
                                        "Models Usage": models_usage,
                                        "Metadata": metadata,
                                    }
                                )

                    elif source == "MagenticOneOrchestrator":
                        with st.chat_message("assistant"):
                            st.markdown(f"**🧠 Orchestrator:** {content}")

                            # Show metadata in expander
                            with st.expander("📋 Orchestrator Details", expanded=False):
                                st.json(
                                    {
                                        "Source": source,
                                        "Type": msg_type,
                                        "Models Usage": models_usage,
                                        "Metadata": metadata,
                                    }
                                )

                    else:
                        # Handle other agent sources
                        with st.chat_message("Assistant"):
                            st.markdown(f"**🤖 {source}:** {content}")

                            # Show metadata in expander
                            with st.expander(f"📋 {source} Details", expanded=False):
                                st.json(
                                    {
                                        "Source": source,
                                        "Type": msg_type,
                                        "Models Usage": models_usage,
                                        "Metadata": metadata,
                                    }
                                )

                    # Add a small delay to make streaming visible
                    await asyncio.sleep(0.1)

                # Now process the final result if we got one
                if final_result:
                    with answer_container:
                        st.divider()
                        st.success("✅ **Task Completed!**")

                        # Extract the final answer
                        messages_list = getattr(final_result, "messages", [])
                        stop_reason = getattr(
                            final_result, "stop_reason", "Task completed"
                        )

                        # Find the last meaningful response from MagenticOneOrchestrator
                        final_answer = None
                        for message in reversed(messages_list):
                            if (
                                getattr(message, "source", "")
                                == "MagenticOneOrchestrator"
                            ):
                                content = getattr(message, "content", "")
                                # Skip the planning messages, get the final summary
                                if not content.startswith(
                                    "\nWe are working to address"
                                ):
                                    final_answer = content
                                    break

                        # Display the clean final result in a highlighted section
                        st.markdown("### 🎯 **Final Answer**")
                        with st.container():
                            st.markdown(
                                f"**Result:** {final_answer}"
                                if final_answer
                                else "Task completed successfully."
                            )

                        # Show completion details
                        st.info(f"🏁 **Completion Reason:** {stop_reason}")
                        st.info(
                            f"📊 **Total Messages Processed:** {len(messages_list)}"
                        )

                        # Option to view full conversation summary
                        with st.expander(
                            "📜 View Complete Message Summary", expanded=False
                        ):
                            st.write(f"**Total Messages:** {len(messages_list)}")

                            for i, message in enumerate(messages_list, 1):
                                source = getattr(message, "source", "unknown")
                                content = getattr(message, "content", str(message))
                                msg_type = getattr(message, "type", "Unknown")

                                st.write(f"**Message {i} - {source} ({msg_type}):**")
                                with st.container():
                                    if len(content) > 200:
                                        st.text_area(
                                            f"Content {i}",
                                            content,
                                            height=100,
                                            disabled=True,
                                        )
                                    else:
                                        st.markdown(content)
                                st.divider()

                else:
                    st.warning(
                        "⚠️ No final result received. Task may have ended unexpectedly."
                    )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

    # Run the async task
    asyncio.run(run_task_with_streaming(task))
