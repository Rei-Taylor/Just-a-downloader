document.addEventListener('alpine:init', () => {
            Alpine.data('app', () => ({
                // Tab control
                activeTab: 'youtube',
                
                // YouTube downloader state
                url: '',
                metadata: null,
                loading: false,
                downloadingVideo: false,
                downloadingAudio: false,
                error: null,
                selectedResolution: '720p',
                
                // General downloader state
                fileUrl: '',
                fileInfo: null,
                fetchingFileInfo: false,
                downloadingFile: false,
                downloadComplete: false,
                progress: 0,
                downloadSpeed: 0,
                remainingTime: 0,
                maxWorkers: 8,
                chunkSize: 1,
                eventSource: null,
                
                progressClass() {
                    if (this.progress < 30) return 'progress-low';
                    if (this.progress < 70) return 'progress-medium';
                    return 'progress-high';
                },
                
                // YouTube downloader methods
                fetchMetadata() {
                    this.resetState();
                    this.loading = true;
                    
                    fetch('/api/metadata', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({url: this.url})
                    })
                    .then(response => {
                        if (!response.ok) throw new Error('Failed to fetch video details');
                        return response.json();
                    })
                    .then(data => {
                        this.metadata = data;
                        this.selectedResolution = data.available_resolutions.includes('720p') 
                            ? '720p' 
                            : data.available_resolutions[0];
                    })
                    .catch(err => {
                        this.error = err.message || 'An error occurred while fetching video info';
                        console.error(err);
                    })
                    .finally(() => {
                        this.loading = false;
                    });
                },
                
                downloadVideo() {
                    this.downloadingVideo = true;
                    this.error = null;
                    
                    fetch('/api/download/video', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ 
                            url: this.url, 
                            resolution: this.selectedResolution 
                        })
                    })
                    .then(response => {
                        if (!response.ok) throw new Error('Failed to download video');
                        return response.json();
                    })
                    .then(() => {
                        this.showNotification('Video downloaded successfully!', 'success');
                    })
                    .catch(err => {
                        this.error = err.message || 'Video download failed';
                        console.error(err);
                    })
                    .finally(() => {
                        this.downloadingVideo = false;
                    });
                },
                
                downloadAudio() {
                    this.downloadingAudio = true;
                    this.error = null;
                    
                    fetch('/api/download/audio', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ url: this.url })
                    })
                    .then(response => {
                        if (!response.ok) throw new Error('Failed to download audio');
                        return response.json();
                    })
                    .then(() => {
                        this.showNotification('Audio downloaded successfully!', 'success');
                    })
                    .catch(err => {
                        this.error = err.message || 'Audio download failed';
                        console.error(err);
                    })
                    .finally(() => {
                        this.downloadingAudio = false;
                    });
                },
                
                resetState() {
                    this.metadata = null;
                    this.error = null;
                },
                
                // General file downloader methods
                getFileDetails() {
                    this.fetchingFileInfo = true;
                    this.error = null;
                    this.fileInfo = null;
                    this.downloadComplete = false;
                    
                    fetch('/api/file/info', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ 
                            url: this.fileUrl,
                            max_workers: this.maxWorkers,
                            chunk_size_mb: this.chunkSize
                        })
                    })
                    .then(response => {
                        if (!response.ok) throw new Error('Failed to get file information');
                        return response.json();
                    })
                    .then(data => {
                        this.fileInfo = data;
                    })
                    .catch(err => {
                        this.error = err.message || 'Failed to get file details';
                        console.error(err);
                    })
                    .finally(() => {
                        this.fetchingFileInfo = false;
                    });
                },
                
                startDownload() {
                    if (this.eventSource) {
                        this.eventSource.close();
                    }
                    
                    this.downloadingFile = true;
                    this.downloadComplete = false;
                    this.progress = 0;
                    this.downloadSpeed = 0;
                    this.remainingTime = 0;
                    this.error = null;
                    
                    // First initiate the download
                    fetch('/api/file/download', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ 
                            url: this.fileUrl,
                            max_workers: this.maxWorkers,
                            chunk_size_mb: this.chunkSize
                        })
                    })
                    .then(response => {
                        if (!response.ok) throw new Error('Failed to start download');
                        return response.json();
                    })
                    .then(data => {
                        // Then connect to the progress stream using the download ID
                        const encodedId = encodeURIComponent(data.download_id);
                        this.eventSource = new EventSource(`/api/file/download/progress?download_id=${encodedId}`);
                        
                        this.eventSource.onmessage = (event) => {
                            const data = JSON.parse(event.data);
                            
                            if (data.status === 'downloading') {
                                this.progress = data.progress;
                                this.downloadSpeed = data.speed;
                                this.remainingTime = data.remaining_seconds;
                            } else if (data.status === 'completed') {
                                this.progress = 100;
                                this.downloadingFile = false;
                                this.downloadComplete = true;
                                this.showNotification(`Download completed successfully! Saved to: ${data.filename}`, 'success');
                                this.eventSource.close();
                            } else if (data.status === 'failed') {
                                this.downloadingFile = false;
                                this.error = data.error || 'Download failed';
                                console.error('Download failed:', data.error);
                                this.eventSource.close();
                            }
                        };
                        
                        this.eventSource.onerror = (err) => {
                            this.downloadingFile = false;
                            this.error = 'Connection error during download';
                            console.error('EventSource error:', err);
                            if (this.eventSource) {
                                this.eventSource.close();
                            }
                        };
                    })
                    .catch(err => {
                        this.downloadingFile = false;
                        this.error = err.message || 'Failed to start download';
                        console.error(err);
                    });
                },
                
                formatNumber(num) {
                    if (!num) return '0';
                    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
                    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
                    return num.toString();
                },
                
                showNotification(message, type = 'info') {
                    alert(message);
                }
            }));
        });