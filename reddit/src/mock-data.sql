-- Insert mock data into the posts table
INSERT INTO posts (upvotes, title, link, username) VALUES
(100, 'How to Train Your Dragon', 'https://example.com/dragon-training', 'user123'),
(250, '10 Tips for Better Coding', 'https://example.com/coding-tips', 'devGuru'),
(75, 'Best Photography Spots in NYC', 'https://example.com/nyc-photography', 'photoguy'),
(300, 'The Ultimate Guide to Fitness', 'https://example.com/fitness-guide', 'fitnessFreak'),
(150, 'Top 5 Python Libraries for Data Science', 'https://example.com/python-libraries', 'dataNerd'),
(200, 'Exploring Space: A Beginner''s Guide', 'https://example.com/space-exploration', 'astroFan'),
(180, 'Understanding Cryptocurrency Basics', 'https://example.com/crypto-basics', 'cryptoGeek'),
(90, 'The Future of AI: What to Expect', 'https://example.com/ai-future', 'aiWizard'),
(50, 'Beginner''s Guide to Web Development', 'https://example.com/web-dev-guide', 'webMaster'),
(400, 'How to Cook the Perfect Steak', 'https://example.com/perfect-steak', 'chefMaster');

-- Insert mock data into the comments table
INSERT INTO comments (post_id, upvotes, text, username) VALUES
(1, 50, 'This is an amazing guide, really helpful!', 'commenter01'),
(1, 30, 'I tried this and it worked perfectly.', 'userX'),
(2, 100, 'Great coding tips! I especially loved number 3.', 'devEnthusiast'),
(2, 25, 'Very informative, thanks for sharing!', 'codeLover'),
(3, 60, 'I visited two of these spots, they are beautiful!', 'photobug'),
(4, 80, 'This fitness guide changed my workout routine completely!', 'gymRat'),
(4, 45, 'The exercises in this guide are killer!', 'fitFanatic'),
(5, 75, 'The Python libraries you mentioned are awesome!', 'dataScientist01'),
(6, 90, 'Space exploration is fascinating, thanks for this guide!', 'astroNerd'),
(7, 35, 'Cryptocurrency is the future, well-explained basics.', 'cryptoInvestor'),
(8, 20, 'Can’t wait to see how AI evolves over the next few years.', 'techLover'),
(8, 45, 'AI is advancing so quickly, great read.', 'aiGeek'),
(9, 10, 'This is a great resource for beginners like me!', 'webNewbie'),
(10, 95, 'Best steak I’ve ever made, thanks for the tips!', 'foodieMaster');
