import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from app.models import WatchHistory, Video

def get_recommendations(user_id):
    # Get all watch history
    history = WatchHistory.query.all()
    
    if not history:
        return Video.query.limit(5).all()
    
    # Create user-video matrix
    data = [(h.user_id, h.video_id) for h in history]
    df = pd.DataFrame(data, columns=['user_id', 'video_id'])
    
    # Create pivot table
    pivot = df.pivot_table(
        index='user_id', 
        columns='video_id', 
        aggfunc=len, 
        fill_value=0
    )
    
    # Calculate similarity
    similarity = cosine_similarity(pivot)
    similarity_df = pd.DataFrame(
        similarity, 
        index=pivot.index, 
        columns=pivot.index
    )
    
    # Get recommendations for user
    if user_id not in similarity_df.index:
        return Video.query.limit(5).all()
    
    similar_users = similarity_df[user_id].sort_values(ascending=False)[1:4].index
    
    watched = df[df['user_id'] == user_id]['video_id'].tolist()
    
    recommended_ids = df[
        (df['user_id'].isin(similar_users)) & 
        (~df['video_id'].isin(watched))
    ]['video_id'].unique()[:5]
    
    recommended_videos = Video.query.filter(
        Video.id.in_(recommended_ids)
    ).all()
    
    if not recommended_videos:
        return Video.query.limit(5).all()
    
    return recommended_videos