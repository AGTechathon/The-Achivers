import random
import time

import pandas as pd
from faicons import icon_svg
from shiny import reactive, req
from shiny.express import input, module, render, ui
from shinymedia import audio_spinner, input_video_clip

from query_bakeoff import chat

ui.tags.style("body { background-color: var(--bs-light); }")


@module
def candidate(input, output, session, model_id, model_name, clip, current_winner):
    # Each model gets its own message history
    messages = []
    model_wins = reactive.value(0)

    ui.h5(model_name)

    # Process the video and chat with the model.
    @reactive.extended_task
    async def process(video_input, messages, session):
        req(video_input)
        with ui.Progress(session=session) as p:
            p.set(message=model_name)
            start_time = time.time_ns()
            return (
                chat(model_id, video_input, messages, p),
                (time.time_ns() - start_time) / 1e9,
            )

    # Kick off the video processing whenever a new video is uploaded.
    @reactive.effect
    def start_process():
        process.cancel()
        process(clip(), messages, session)


    @reactive.effect
    @reactive.event(input.vote)
    def vote():
        # The user voted for this model! Record that result.
        current_winner.set(model_id)
        model_wins.set(model_wins() + 1)

    @reactive.effect
    @reactive.event(input.unvote)
    def unvote():
        # The user made a mistake, undo the vote.
        current_winner.set(None)
        model_wins.set(model_wins() - 1)

    # Make the current number of wins for this model available to the rest of
    # the app.
    return model_wins


with ui.layout_columns(class_="my-4"):
    input_video_clip("clip", reset_on_record=True)
    with ui.card(fill=True, height="250px"):

        @render.plot
        def plot_leader():
            df = results_df()
            # Make a horizontal bar chart of the results using matplotlib, setting the x axis to start at 0 and end at 5 or the max value
            ax = df.plot.barh(x="Model", y="Wins", legend=False)
            ax.set_xlim(0, max(5, df["Wins"].max()))
            return ax


current_winner = reactive.value(None)
candidates = {}


@reactive.effect
def reset_winner():
    if input.clip() is None:
        current_winner.set(None)


with ui.panel_conditional("input.clip"):
    with ui.layout_columns(class_="my-4"):
        with ui.card():
            candidates["GPT-4o"] = candidate(
                "one", "gpt-4o", "GPT-4o", input.clip, current_winner
            )
        with ui.card():
            candidates["GPT-4"] = candidate(
                "two", "gpt-4-vision-preview", "GPT-4", input.clip, current_winner
            )
        with ui.card():
            candidates["LLaVA (7B)"] = candidate(
                "three", "llava:7b", "LLaVA (7B)", input.clip, current_winner
            )


@reactive.calc
def results_df():
    snapshot = {k: v() for k, v in candidates.items()}
    return pd.DataFrame(snapshot.items(), columns=["Model", "Wins"])
